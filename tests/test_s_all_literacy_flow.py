"""
통합 시나리오 — 로그인 + 메인 보상/오늘의 어휘 + 술술 읽기 검증
=================================================================

BrowserStack App Automate 버전
  - 디바이스: Samsung Galaxy Tab S11 / Android 16.0
  - Appium 서버: BrowserStack hub

환경변수 (GitHub Secrets):
  BROWSERSTACK_USERNAME   : BrowserStack 계정 username
  BROWSERSTACK_ACCESS_KEY : BrowserStack access key
  BROWSERSTACK_APP_URL    : BrowserStack에 업로드된 APK URL (bs://...)
  TEST_ID                 : 앱 로그인 아이디
  TEST_PW                 : 앱 로그인 비밀번호

실행 방법:
  pytest tests/test_s_all_literacy_flow.py -v -s

전체 흐름:
  [S01] 앱 실행 / 로그인 / 메인 진입
  [S023] 나의 랭킹 → 나의 보상 → 메인 복귀
  [S023] 오늘의 어휘 3문제 수행 → 리그 포인트 +5P 확인
  [S022] 술술 읽기 진입 → 독서 탐험 → 훈련1 → 훈련2 → 메인 복귀
"""

import os
import re
import sys
import time
import pytest
from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.remote.client_config import ClientConfig

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import TEST_ID, TEST_PW
from helpers.training_types import handle_training


# ──────────────────────────────────────────────────────────
# BrowserStack / Appium 설정
# ──────────────────────────────────────────────────────────
APPIUM_SERVER = "https://hub-cloud.browserstack.com/wd/hub"

PKG = "com.kyowon.literacy.store"
MAIN_ACTIVITY = "com.kyowon.literacy.ui.intro.activity.IntroActivity"

DEFAULT_TIMEOUT = 10
SHORT_TIMEOUT = 2
LOADING_CHECK_TIMEOUT = 0.8
LOADING_TIMEOUT = 45
MAIN_TIMEOUT = 15
STUDY_TIMEOUT = 120

CLICK_DELAY = 0.35
QUESTION_ADVANCE_TIMEOUT = 7
ANSWER_SETTLE_DELAY = 0.9


# ──────────────────────────────────────────────────────────
# Driver Fixture
# ──────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    bs_username = os.environ["BROWSERSTACK_USERNAME"]
    bs_access_key = os.environ["BROWSERSTACK_ACCESS_KEY"]
    bs_app_url = os.environ["BROWSERSTACK_APP_URL"]

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Samsung Galaxy Tab S11"
    options.platform_version = "16.0"

    options.set_capability("app", bs_app_url)
    options.set_capability("appPackage", PKG)
    options.set_capability("appActivity", MAIN_ACTIVITY)
    options.set_capability("noReset", False)
    options.set_capability("newCommandTimeout", 300)
    options.set_capability("autoGrantPermissions", True)

    options.set_capability("bstack:options", {
        "userName": bs_username,
        "accessKey": bs_access_key,
        "projectName": "Kyowon Literacy",
        "buildName": f"Literacy-CI-{os.environ.get('GITHUB_RUN_NUMBER', 'local')}",
        "sessionName": "All Literacy Flow",
        "deviceLogs": True,
        "appiumLogs": True,
        "video": True,
        "networkLogs": True,
        "idleTimeout": 300,
    })

    bs_hub_url = "https://hub-cloud.browserstack.com/wd/hub"
    client_config = ClientConfig(
        remote_server_addr=bs_hub_url,
        username=bs_username,
        password=bs_access_key,
    )
    drv = webdriver.Remote(
        command_executor=AppiumConnection(client_config=client_config),
        options=options
    )

    print("\n드라이버 연결 성공 (BrowserStack)")
    yield drv
    drv.quit()
    print("\n드라이버 세션 종료")


# ──────────────────────────────────────────────────────────
# 공통 Appium helper
# ──────────────────────────────────────────────────────────
def full_id(resource_id: str) -> str:
    if resource_id.startswith("android:id/") or ":id/" in resource_id:
        return resource_id
    return f"{PKG}:id/{resource_id}"


def wait_id(drv, resource_id, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout, poll_frequency=0.2).until(
            EC.presence_of_element_located((AppiumBy.ID, full_id(resource_id)))
        )
    except TimeoutException:
        return None


def wait_id_clickable(drv, resource_id, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout, poll_frequency=0.2).until(
            EC.element_to_be_clickable((AppiumBy.ID, full_id(resource_id)))
        )
    except TimeoutException:
        return None


def wait_text(drv, text, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout, poll_frequency=0.2).until(
            EC.presence_of_element_located((AppiumBy.XPATH, f'//*[@text="{text}"]'))
        )
    except TimeoutException:
        return None


def wait_gone(drv, resource_id, timeout=LOADING_TIMEOUT):
    try:
        WebDriverWait(drv, timeout, poll_frequency=0.2).until_not(
            EC.presence_of_element_located((AppiumBy.ID, full_id(resource_id)))
        )
    except TimeoutException:
        pass


def find_id(drv, resource_id):
    try:
        return drv.find_element(AppiumBy.ID, full_id(resource_id))
    except NoSuchElementException:
        return None


def find_ids(drv, resource_id):
    return drv.find_elements(AppiumBy.ID, full_id(resource_id))


def wait_full_id_clickable(drv, full_resource_id, timeout=DEFAULT_TIMEOUT):
    locators = [
        (AppiumBy.ID, full_resource_id),
        (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceId("{full_resource_id}")'),
        (AppiumBy.XPATH, f'//*[@resource-id="{full_resource_id}"]'),
    ]
    for by, value in locators:
        try:
            return WebDriverWait(drv, timeout, poll_frequency=0.2).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            continue
    return None


def tap_element_center(drv, el, label="요소"):
    rect = el.rect
    x = int(rect["x"] + rect["width"] / 2)
    y = int(rect["y"] + rect["height"] / 2)
    drv.execute_script("mobile: clickGesture", {"x": x, "y": y})
    print(f"  {label} 좌표 탭 ({x}, {y})")
    time.sleep(CLICK_DELAY)


def click_id(drv, resource_id, label=None, timeout=DEFAULT_TIMEOUT, use_center_fallback=True):
    label = label or resource_id

    el = wait_id_clickable(drv, resource_id, timeout=timeout)
    if el:
        try:
            el.click()
            print(f"  {label} 클릭")
            time.sleep(CLICK_DELAY)
            return True
        except Exception:
            if use_center_fallback:
                tap_element_center(drv, el, label)
                return True
            raise

    if use_center_fallback:
        el = wait_id(drv, resource_id, timeout=timeout)
        if el:
            tap_element_center(drv, el, label)
            return True

    return False


def click_full_id(drv, full_resource_id, label, timeout=DEFAULT_TIMEOUT):
    el = wait_full_id_clickable(drv, full_resource_id, timeout=timeout)
    assert el is not None, f"{label}({full_resource_id}) 버튼을 찾을 수 없음"
    el.click()
    print(f"  {label} 클릭")
    time.sleep(CLICK_DELAY)
    return True


def handle_loading(drv):
    loading = wait_id(drv, "layout_progress", timeout=LOADING_CHECK_TIMEOUT)
    if loading:
        print("  로딩 대기 중...")
        wait_gone(drv, "layout_progress", timeout=LOADING_TIMEOUT)
        time.sleep(0.8)


def ensure_main(drv, timeout=MAIN_TIMEOUT):
    handle_loading(drv)
    main = wait_id(drv, "container_main", timeout=timeout)
    assert main is not None, "메인 화면(container_main) 미노출"
    print("  메인 화면 확인 (container_main)")
    return main


def back_to_main(drv, max_try=5):
    for attempt in range(1, max_try + 1):
        if find_id(drv, "container_main"):
            print("  메인 화면 복귀 확인")
            return True

        if click_id(drv, "btnBack", "뒤로가기(btnBack)", timeout=1):
            handle_loading(drv)
            continue

        if click_id(drv, "btn_book_list_back", "뒤로가기(btn_book_list_back)", timeout=1):
            handle_loading(drv)
            continue

        if click_id(drv, "btn_alert_negative", "닫기/취소(btn_alert_negative)", timeout=1):
            handle_loading(drv)
            continue

        print(f"  시스템 BACK 입력 ({attempt}/{max_try})")
        drv.back()
        time.sleep(CLICK_DELAY)
        handle_loading(drv)

    main = wait_id(drv, "container_main", timeout=MAIN_TIMEOUT)
    assert main is not None, "메인 화면(container_main) 복귀 실패"
    print("  메인 화면 복귀 확인")
    return True


# ──────────────────────────────────────────────────────────
# 로그인 / 초기 팝업 helper
# ──────────────────────────────────────────────────────────
def handle_permission_guide_popup(drv):
    popup = wait_id(drv, "txt_title", timeout=5)
    if popup and "권한" in popup.text:
        print(f"  권한 안내 팝업 발견: {popup.text}")
        assert click_id(drv, "btn_confirm", "권한 안내 확인(btn_confirm)", timeout=5)
        print("  시스템 권한 팝업은 autoGrantPermissions=True로 자동 허용")
        time.sleep(1.2)
        return True

    print("  권한 안내 팝업 없음 → 건너뜀")
    return False


def login_if_needed(drv):
    if wait_id(drv, "container_main", timeout=3):
        print("  이미 메인 화면 상태 → 로그인 생략")
        return True

    id_field = wait_id(drv, "et_id", timeout=DEFAULT_TIMEOUT)
    assert id_field is not None, "로그인 화면(et_id) 미노출"

    version_el = wait_id(drv, "txt_app_version", timeout=2)
    if version_el:
        print(f"  앱 버전: {version_el.text}")

    id_field.clear()
    id_field.send_keys(TEST_ID)
    print(f"  아이디 입력: {TEST_ID}")

    pw_field = wait_id(drv, "et_pw", timeout=DEFAULT_TIMEOUT)
    assert pw_field is not None, "비밀번호 입력 필드(et_pw) 미노출"
    pw_field.clear()
    pw_field.send_keys(TEST_PW)
    print(f"  비밀번호 입력: {'*' * len(TEST_PW)}")

    assert click_id(drv, "btn_login", "로그인 버튼(btn_login)", timeout=DEFAULT_TIMEOUT)
    handle_loading(drv)

    return True


def handle_welcome_popup_if_any(drv):
    popup = wait_id(drv, "text_alert_message", timeout=8)
    if popup:
        print(f"  로그인/알림 팝업 발견: {popup.text[:30]}...")
        if click_id(drv, "btn_alert_positive", "팝업 확인(btn_alert_positive)", timeout=5):
            handle_loading(drv)
            return True

    print("  로그인 성공 팝업 없음 → 건너뜀")
    return False


def handle_tutorial_if_any(drv):
    tutorial = wait_id(drv, "img_tuto", timeout=4)
    if tutorial:
        print("  튜토리얼 화면 발견")
        if click_id(drv, "btn_close", "튜토리얼 닫기(btn_close)", timeout=3):
            return True
        for _ in range(5):
            if click_id(drv, "btn_next", "튜토리얼 다음(btn_next)", timeout=1):
                continue
            if click_id(drv, "btn_start", "튜토리얼 시작(btn_start)", timeout=1):
                break
        return True

    print("  튜토리얼 없음 → 건너뜀")
    return False


def handle_level_test_popup_if_any(drv):
    title = wait_id(drv, "text_alert_title", timeout=4)
    if title and "평가" in title.text:
        print(f"  문해력 실전 평가 팝업 발견: {title.text}")
        if click_id(drv, "btn_alert_negative", "하지 않을래요(btn_alert_negative)", timeout=5):
            return True

    close = wait_id(drv, "btn_level_test_close", timeout=2)
    if close:
        close.click()
        print("  레벨 테스트 화면 닫기")
        time.sleep(CLICK_DELAY)
        return True

    print("  문해력 실전 평가 팝업 없음 → 건너뜀")
    return False


# ──────────────────────────────────────────────────────────
# S023 오늘의 어휘 / 보상 helper
# ──────────────────────────────────────────────────────────
def parse_point(text: str):
    if not text:
        return None
    match = re.search(r"(\d+)", text.replace(",", ""))
    return int(match.group(1)) if match else None


def get_league_point(drv):
    el = wait_id(drv, "txt_league_point", timeout=DEFAULT_TIMEOUT)
    assert el is not None, "리그 포인트(txt_league_point) 미노출"
    point = parse_point(el.text)
    assert point is not None, f"리그 포인트 숫자 파싱 실패: [{el.text}]"
    print(f"  현재 리그 포인트: {point}P")
    return point


def get_question_text(drv):
    el = find_id(drv, "question_txt")
    if not el:
        return None
    try:
        return el.text.strip()
    except StaleElementReferenceException:
        return None


def wait_question_advanced(drv, before_text, question_no, timeout=QUESTION_ADVANCE_TIMEOUT):
    if question_no >= 3:
        time.sleep(ANSWER_SETTLE_DELAY)
        return "settled"

    end_time = time.time() + timeout
    last_text = before_text

    while time.time() < end_time:
        current = get_question_text(drv)
        if current:
            last_text = current
        if current and current != before_text:
            return "changed"
        time.sleep(0.25)

    time.sleep(ANSWER_SETTLE_DELAY)
    return f"timeout_same_question:[{last_text}]"


def click_first_quiz_option(drv, question_no):
    question = get_question_text(drv)
    print(f"  {question_no}번 문제: [{question}]")

    options = find_ids(drv, "btn_quiz_option")
    visible_options = [el for el in options if el.is_displayed()]
    assert visible_options, f"{question_no}번 문제 보기(btn_quiz_option) 미노출"

    selected = visible_options[0]
    try:
        selected_text = selected.text.strip()
    except Exception:
        selected_text = ""

    try:
        selected.click()
        print(f"  {question_no}번 보기 선택: [{selected_text}]")
        time.sleep(CLICK_DELAY)
    except Exception:
        tap_element_center(drv, selected, f"{question_no}번 보기")

    status = wait_question_advanced(drv, question, question_no)
    print(f"  {question_no}번 선택 후 상태: {status}")


def handle_today_voca_result_popup_if_any(drv):
    for rid, label in [
        ("btn_alert_positive", "결과 확인(btn_alert_positive)"),
        ("btn_confirm", "결과 확인(btn_confirm)"),
        ("btn_popup_close", "결과 닫기(btn_popup_close)"),
    ]:
        if click_id(drv, rid, label, timeout=1):
            handle_loading(drv)
            return True
    return False


# ──────────────────────────────────────────────────────────
# S022 술술 읽기 helper
# ──────────────────────────────────────────────────────────
def handle_posture_popup_by_image_button(drv, wait=3):
    preview = wait_id(drv, "view_face_preview", timeout=wait)
    status = find_id(drv, "txt_check_fluency")
    notice = find_id(drv, "notice_txt")

    if not preview and not status and not notice:
        return False

    try:
        btn = WebDriverWait(drv, wait, poll_frequency=0.2).until(
            EC.element_to_be_clickable((AppiumBy.CLASS_NAME, "android.widget.ImageButton"))
        )
        btn.click()
        print("  바른자세 팝업 X(android.widget.ImageButton) 클릭")
        time.sleep(CLICK_DELAY)
        return True
    except TimeoutException:
        print("  바른자세 팝업은 감지됐으나 X(android.widget.ImageButton) 미노출")
        return False


def handle_guide_popup(drv, popup_wait=3):
    popup = wait_id(drv, "btn_skip_today", timeout=popup_wait)
    if not popup:
        return False

    print("  학습 가이드 팝업 감지")

    for _ in range(10):
        page_el = find_id(drv, "txt_page")
        if page_el and "/" in page_el.text:
            current, total = page_el.text.strip().split("/")
            print(f"  팝업 페이지: {page_el.text.strip()}")
            if current.strip() == total.strip():
                break

            next_btn = wait_id_clickable(drv, "btn_next", timeout=2)
            if next_btn:
                next_btn.click()
                time.sleep(0.5)
            else:
                break
        else:
            break

    close_btn = wait_id_clickable(drv, "btn_popup_close", timeout=5)
    if close_btn:
        close_btn.click()
        print("  가이드 팝업 닫기(btn_popup_close) 클릭")
        time.sleep(0.8)
        return True

    print("  btn_popup_close 미노출")
    return False


def run_training(drv, tc_label, proceed_next=True):
    screen = wait_id(drv, "layout_learning_fragment", timeout=DEFAULT_TIMEOUT)
    assert screen is not None, f"{tc_label} 훈련 화면(layout_learning_fragment) 미노출"
    print(f"  {tc_label} 훈련 화면 노출 확인")

    handle_guide_popup(drv, popup_wait=3)

    training_name = handle_training(drv)
    print(f"  {tc_label} 처리 완료: [{training_name}]")

    refresh = wait_id(drv, "layout_refresh_ui", timeout=DEFAULT_TIMEOUT)
    if refresh:
        print(f"  {tc_label} 완료 확인 (layout_refresh_ui)")
    else:
        print(f"  {tc_label} layout_refresh_ui 미노출")

    if proceed_next:
        btn_next = wait_id_clickable(drv, "btnNext", timeout=DEFAULT_TIMEOUT)
        if btn_next:
            btn_next.click()
            print(f"  {tc_label} btnNext 클릭")
            time.sleep(1.2)
            handle_loading(drv)
        else:
            print(f"  {tc_label} btnNext 미노출")
    else:
        print(f"  {tc_label} btnNext 생략 → 완료 화면 유지")


# ──────────────────────────────────────────────────────────
# 통합 테스트 시나리오
# ──────────────────────────────────────────────────────────
class TestAllLiteracyFlow:
    """통합: 로그인 → 메인 기능 → 오늘의 어휘 → 술술 읽기"""

    _initial_study_progress = None

    # ========== S01 로그인 / 메인 진입 ==========
    def test_01_app_start_and_permission_popup(self, driver):
        print("\n[TC-01] 앱 실행 및 권한 안내 팝업 처리")
        handle_loading(driver)
        handle_permission_guide_popup(driver)

    def test_02_login(self, driver):
        print("\n[TC-02] 로그인")
        login_if_needed(driver)
        handle_welcome_popup_if_any(driver)

    def test_03_optional_popups_after_login(self, driver):
        print("\n[TC-03] 로그인 후 선택 팝업 처리")
        handle_tutorial_if_any(driver)
        handle_level_test_popup_if_any(driver)
        handle_loading(driver)

    def test_04_main_screen_visible(self, driver):
        print("\n[TC-04] 메인 화면 진입 확인")
        ensure_main(driver)

        name_el = wait_id(driver, "txt_name", timeout=3)
        if name_el:
            print(f"  사용자: {name_el.text}")

        report_el = wait_id(driver, "txt_report_name", timeout=3)
        if report_el:
            print(f"  학습 리포트 영역: {report_el.text}")

    # ========== S023 나의 보상 ==========
    def test_05_my_ranking_reward_back_to_main(self, driver):
        print("\n[TC-05] 나의 랭킹 → 나의 보상 → 메인 복귀")
        ensure_main(driver)

        clicked = click_id(
            driver,
            "left_center_layout",
            "나의 랭킹 영역(left_center_layout)",
            timeout=DEFAULT_TIMEOUT,
            use_center_fallback=True,
        )
        assert clicked, "나의 랭킹 영역(left_center_layout)을 찾을 수 없음"
        handle_loading(driver)

        if click_id(driver, "view_go_my_reward", "나의 보상(view_go_my_reward)", timeout=2):
            handle_loading(driver)
        elif click_id(driver, "btn_reward_management", "나의 보상(btn_reward_management)", timeout=2):
            handle_loading(driver)
        else:
            print("  나의 보상 진입 버튼 미노출 → 현재 화면에서 보상 화면 여부 확인")

        reward_screen = (
            wait_text(driver, "포인트 이력", timeout=2)
            or wait_id(driver, "btn_reward_management", timeout=1)
            or wait_id(driver, "txt_accumulatedpoint", timeout=1)
            or wait_id(driver, "btnBack", timeout=1)
        )
        assert reward_screen is not None, "나의 보상 화면 진입 확인 실패"
        print("  나의 보상 화면 확인")

        back_to_main(driver)
        ensure_main(driver)

    # ========== S023 오늘의 어휘 ==========
    def test_06_today_vocabulary_point_plus_5(self, driver):
        print("\n[TC-06] 오늘의 어휘 3문제 수행 → 리그 포인트 +5P 확인")
        ensure_main(driver)

        before_point = get_league_point(driver)

        today_voca = wait_id(driver, "item_today_vocabulary", timeout=DEFAULT_TIMEOUT)
        assert today_voca is not None, "오늘의 어휘 영역(item_today_vocabulary) 미노출"

        question = wait_id(driver, "question_txt", timeout=DEFAULT_TIMEOUT)
        assert question is not None, "오늘의 어휘 문제(question_txt) 미노출"
        print("  오늘의 어휘 영역 확인")

        for i in range(1, 4):
            click_first_quiz_option(driver, i)

        handle_today_voca_result_popup_if_any(driver)
        handle_loading(driver)
        ensure_main(driver)

        expected_point = before_point + 5
        final_point = None
        end_time = time.time() + 8

        while time.time() < end_time:
            final_point = get_league_point(driver)
            if final_point == expected_point:
                break
            print(f"  포인트 반영 대기: 현재 {final_point}P / 기대 {expected_point}P")
            time.sleep(0.5)

        assert final_point == expected_point, (
            f"오늘의 어휘 완료 후 리그 포인트 +5P 반영 실패: "
            f"수행 전 {before_point}P, 수행 후 {final_point}P, 기대 {expected_point}P"
        )
        print(f"  리그 포인트 +5P 확인: {before_point}P → {final_point}P")

    # ========== S022 술술 읽기 ==========
    def test_07_enter_study(self, driver):
        print("\n[TC-07] 술술 읽기 진입")
        ensure_main(driver)

        first_class = find_id(driver, "txt_firstclass")
        if first_class:
            print(f"  오늘의 술술 읽기: {first_class.text}")

        progress_els = driver.find_elements(AppiumBy.ID, full_id("txt_progress_percentage"))
        if progress_els:
            TestAllLiteracyFlow._initial_study_progress = progress_els[0].text.strip()
            print(f"  학습 전 진행률: {TestAllLiteracyFlow._initial_study_progress}%")

        btn = wait_id_clickable(driver, "btn_main_first", timeout=DEFAULT_TIMEOUT)
        assert btn is not None, "btn_main_first 버튼을 찾을 수 없음"
        btn.click()
        print("  btn_main_first 클릭")
        time.sleep(1.5)
        handle_loading(driver)
        handle_guide_popup(driver, popup_wait=3)

    def test_08_reading_explore(self, driver):
        print("\n[TC-08] 독서 탐험")
        handle_guide_popup(driver, popup_wait=3)

        book_cover = wait_id(driver, "layout_book_cover", timeout=DEFAULT_TIMEOUT)
        assert book_cover is not None, "독서 탐험 화면(layout_book_cover) 미노출"
        print("  layout_book_cover 확인")

        title_el = find_id(driver, "txt_book_title")
        if title_el:
            print(f"  책 제목: [{title_el.text.strip()}]")

        btn_start = wait_id_clickable(driver, "btn_start", timeout=DEFAULT_TIMEOUT)
        assert btn_start is not None, "독서 시작(btn_start) 버튼을 찾을 수 없음"
        print(f"  독서 시작(btn_start) 클릭: [{btn_start.text}]")
        btn_start.click()
        time.sleep(1.5)

        print(f"  독서 끝 버튼 대기 (최대 {STUDY_TIMEOUT}초)...")
        btn_end = wait_text(driver, "독서 끝", timeout=STUDY_TIMEOUT)
        if btn_end:
            btn_end.click()
            print("  독서 끝 버튼 클릭")
            time.sleep(1.2)
        else:
            print("  독서 끝 버튼 미노출 → layout_refresh_ui 직접 대기")

        refresh = wait_id(driver, "layout_refresh_ui", timeout=DEFAULT_TIMEOUT)
        assert refresh is not None, "독서 완료(layout_refresh_ui) 미노출"
        print("  독서 완료 확인 (layout_refresh_ui)")

        btn_next = wait_id_clickable(driver, "btnNext", timeout=DEFAULT_TIMEOUT)
        assert btn_next is not None, "btnNext 버튼을 찾을 수 없음"
        btn_next.click()
        print("  btnNext 클릭")
        time.sleep(1.2)
        handle_loading(driver)

    def test_09_posture_check_popup(self, driver):
        print("\n[TC-09] 바른자세 팝업 처리 (선택적)")
        result = handle_posture_popup_by_image_button(driver, wait=3)
        if result:
            print("  바른자세 팝업 닫기 완료")
        else:
            print("  바른자세 팝업 미노출 → 건너뜀")

    def test_10_guide_popup_before_training(self, driver):
        print("\n[TC-10] 훈련 전 학습 가이드 팝업 처리 (선택적)")
        result = handle_guide_popup(driver, popup_wait=3)
        if result:
            print("  가이드 팝업 처리 완료")
        else:
            print("  가이드 팝업 미노출 → 건너뜀")

    def test_11_training_1(self, driver):
        print("\n[TC-11] 술술 읽기 훈련1")
        run_training(driver, "훈련1", proceed_next=True)

    def test_12_training_2(self, driver):
        print("\n[TC-12] 술술 읽기 훈련2")
        run_training(driver, "훈련2", proceed_next=False)

    def test_13_back_to_main_after_study(self, driver):
        print("\n[TC-13] btnOpen → btn_exit → 메인 복귀")

        click_full_id(
            driver,
            "com.kyowon.literacy.store:id/btnOpen",
            "메뉴(btnOpen)",
            timeout=DEFAULT_TIMEOUT,
        )

        exit_btn = wait_id_clickable(driver, "btn_exit", timeout=DEFAULT_TIMEOUT)
        assert exit_btn is not None, "btn_exit 버튼을 찾을 수 없음"
        exit_btn.click()
        print("  나가기(btn_exit) 클릭")
        time.sleep(CLICK_DELAY)

        confirm = wait_id_clickable(driver, "btn_alert_positive", timeout=5)
        if confirm:
            confirm.click()
            print("  나가기 확인(btn_alert_positive) 클릭")
            time.sleep(1.5)
        else:
            print("  나가기 확인 팝업 미노출")

        handle_loading(driver)

        main = wait_id(driver, "container_main", timeout=STUDY_TIMEOUT)
        assert main is not None, "메인 화면(container_main) 복귀 실패"
        print("  메인 화면 복귀 확인")

        name_el = find_id(driver, "txt_name")
        if name_el:
            print(f"  사용자: {name_el.text}")

        progress_els = driver.find_elements(AppiumBy.ID, full_id("txt_progress_percentage"))
        if progress_els:
            final = progress_els[0].text.strip()
            print(f"  학습 후 진행률: {final}%")
            if TestAllLiteracyFlow._initial_study_progress:
                if final != TestAllLiteracyFlow._initial_study_progress:
                    print(f"  진행률 변화: {TestAllLiteracyFlow._initial_study_progress}% → {final}%")
                else:
                    print(f"  진행률 미변화: {final}%")

        if find_id(driver, "btn_mark_1"):
            print("  학습 완료 마크(btn_mark_1) 확인")
        else:
            print("  btn_mark_1 미노출 (진행 중 또는 이미 완료 상태)")

        print("\n통합 시나리오 완료")
