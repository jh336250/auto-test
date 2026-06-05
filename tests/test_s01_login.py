"""
시나리오 S01 — 앱 실행 · 로그인 · 메인 진입
==============================================
BrowserStack App Automate 버전
  - 디바이스: Samsung Galaxy Tab S11 / Android 16.0

커버 범위:
  TC-01. 앱 접근 권한 허용 안내 팝업 처리
  TC-02. 로그인 화면 노출 확인
  TC-03. 아이디 / 비밀번호 입력
  TC-04. 로그인 버튼 클릭
  TC-05. 로그인 성공 팝업 처리
  TC-06. 튜토리얼 화면 처리 (선택적)
  TC-07. 문해력 실전 평가 알림 팝업 처리 (선택적)
  TC-08. 메인 화면 진입 확인
  TC-09. 햄버거 메뉴 열기
  TC-10. 설정 화면 진입
  TC-11. 로그아웃 클릭
  TC-12. 로그인 화면 복귀 확인
"""

import sys
import os
import pytest
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.client_config import ClientConfig
from selenium.common.exceptions import TimeoutException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import TEST_ID, TEST_PW

# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────
PKG           = "com.kyowon.literacy.store"
MAIN_ACTIVITY = "com.kyowon.literacy.ui.intro.activity.IntroActivity"
BS_HUB_URL    = "https://hub-cloud.browserstack.com/wd/hub"

DEFAULT_TIMEOUT = 15
LOADING_TIMEOUT = 60


# ──────────────────────────────────────────────
# Fixture
# ──────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    bs_username   = os.environ["BROWSERSTACK_USERNAME"]
    bs_access_key = os.environ["BROWSERSTACK_ACCESS_KEY"]
    bs_app_url    = os.environ["BROWSERSTACK_APP_URL"]

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name   = "Samsung Galaxy Tab S11"
    options.platform_version = "16.0"

    options.set_capability("app",                bs_app_url)
    options.set_capability("appPackage",         PKG)
    options.set_capability("appActivity",        MAIN_ACTIVITY)
    options.set_capability("noReset",            False)
    options.set_capability("newCommandTimeout",  300)
    options.set_capability("autoGrantPermissions", True)

    options.set_capability("bstack:options", {
        "userName":        bs_username,
        "accessKey":       bs_access_key,
        "projectName":     "Kyowon Literacy",
        "buildName":       f"S01-Login-{os.environ.get('GITHUB_RUN_NUMBER', 'local')}",
        "sessionName":     "S01 Login Flow",
        "deviceLogs":      True,
        "appiumLogs":      True,
        "video":           True,
        "networkLogs":     True,
        "idleTimeout":     300,
        "deviceOrientation": "landscape",
    })

    client_config = ClientConfig(
        remote_server_addr=BS_HUB_URL,
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


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────
def wait_id(drv, resource_id, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, f"{PKG}:id/{resource_id}")
            )
        )
    except TimeoutException:
        return None


def wait_text(drv, text, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, f'//*[@text="{text}"]')
            )
        )
    except TimeoutException:
        return None


def wait_gone(drv, resource_id, timeout=LOADING_TIMEOUT):
    try:
        WebDriverWait(drv, timeout).until_not(
            EC.presence_of_element_located(
                (AppiumBy.ID, f"{PKG}:id/{resource_id}")
            )
        )
    except TimeoutException:
        pass


# ──────────────────────────────────────────────
# 테스트 케이스
# ──────────────────────────────────────────────
class TestS01Login:
    """S01: 앱 실행 → 로그인 → 메인 진입"""

    def test_01_handle_permission_guide_popup(self, driver):
        print("\n[TC-01] 앱 접근 권한 허용 안내 팝업 처리 (선택적)")

        loading = wait_id(driver, "layout_progress", timeout=5)
        if loading:
            print("  인트로 로딩 대기 중...")
            wait_gone(driver, "layout_progress")
            time.sleep(1.0)

        popup = wait_id(driver, "txt_title", timeout=10)
        if popup and "권한" in popup.text:
            print(f"  권한 안내 팝업 발견: {popup.text}")
            confirm_btn = wait_id(driver, "btn_confirm", timeout=5)
            assert confirm_btn is not None, "btn_confirm 버튼을 찾을 수 없음"
            confirm_btn.click()
            print("  확인 버튼 클릭")
            time.sleep(2.0)
        else:
            print("  권한 안내 팝업 없음 → 건너뜀")

    def test_02_login_screen_visible(self, driver):
        print("\n[TC-02] 로그인 화면 노출 확인")

        id_field = wait_id(driver, "et_id", timeout=DEFAULT_TIMEOUT)
        assert id_field is not None, "로그인 화면(et_id)이 표시되지 않음"

        version_el = wait_id(driver, "txt_app_version", timeout=5)
        if version_el:
            print(f"  앱 버전 확인: {version_el.text}")

        print("  로그인 화면 노출 확인")

    def test_03_input_credentials(self, driver):
        print("\n[TC-03] 아이디 / 비밀번호 입력")

        id_field = wait_id(driver, "et_id")
        assert id_field is not None, "et_id 필드 없음"
        id_field.clear()
        id_field.send_keys(TEST_ID)
        print(f"  아이디 입력: {TEST_ID}")

        pw_field = wait_id(driver, "et_pw")
        assert pw_field is not None, "et_pw 필드 없음"
        pw_field.clear()
        pw_field.send_keys(TEST_PW)
        print(f"  비밀번호 입력: {'*' * len(TEST_PW)}")

    def test_04_click_login_button(self, driver):
        print("\n[TC-04] 로그인 버튼 클릭")

        btn = wait_id(driver, "btn_login")
        assert btn is not None, "btn_login 버튼 없음"
        btn.click()
        print("  로그인 버튼(들어가기) 클릭")
        time.sleep(2.0)

        loading = wait_id(driver, "layout_progress", timeout=5)
        if loading:
            print("  로그인 처리 로딩 대기 중...")
            wait_gone(driver, "layout_progress")
            time.sleep(1.0)

    def test_05_handle_welcome_popup(self, driver):
        print("\n[TC-05] 로그인 성공 팝업(반가워요!) 처리")

        popup = wait_id(driver, "text_alert_message", timeout=DEFAULT_TIMEOUT)
        assert popup is not None, "로그인 성공 팝업(text_alert_message)이 표시되지 않음"
        print(f"  팝업 발견: {popup.text[:20]}...")

        confirm_btn = wait_id(driver, "btn_alert_positive", timeout=5)
        assert confirm_btn is not None, "팝업 확인 버튼(btn_alert_positive)을 찾을 수 없음"
        confirm_btn.click()
        print("  확인 버튼 클릭")
        time.sleep(1.5)

    def test_06_handle_tutorial(self, driver):
        print("\n[TC-06] 튜토리얼 화면 처리 (선택적)")

        tutorial = wait_id(driver, "img_tuto", timeout=5)
        if tutorial:
            print("  튜토리얼 화면 발견")
            close_btn = wait_id(driver, "btn_close", timeout=5)
            if close_btn:
                close_btn.click()
                print("  튜토리얼 닫기 버튼 클릭")
                time.sleep(1.5)
        else:
            print("  튜토리얼 없음 → 건너뜀")

    def test_07_handle_level_test_popup(self, driver):
        print("\n[TC-07] 문해력 실전 평가 알림 팝업 처리 (선택적)")

        popup_title = wait_id(driver, "text_alert_title", timeout=5)
        if popup_title and "평가" in popup_title.text:
            print(f"  팝업 발견: {popup_title.text}")
            skip_btn = wait_id(driver, "btn_alert_negative", timeout=5)
            if skip_btn:
                skip_btn.click()
                print("  '하지 않을래요' 클릭")
                time.sleep(1.5)

            level_test_close = wait_id(driver, "btn_level_test_close", timeout=5)
            if level_test_close:
                level_test_close.click()
                print("  레벨 테스트 화면 닫기")
                time.sleep(1.5)
        else:
            print("  문해력 평가 팝업 없음 → 건너뜀")

    def test_08_main_screen_visible(self, driver):
        print("\n[TC-08] 메인 화면 진입 확인")

        loading = wait_id(driver, "layout_progress", timeout=5)
        if loading:
            print("  메인 화면 로딩 대기 중...")
            wait_gone(driver, "layout_progress")
            time.sleep(1.5)

        main = wait_id(driver, "container_main", timeout=DEFAULT_TIMEOUT)
        assert main is not None, "메인 화면(container_main) 진입 실패"
        print("  메인 화면 확인")

        name_el = wait_id(driver, "txt_name", timeout=5)
        if name_el:
            print(f"  로그인 사용자: {name_el.text}")

    def test_09_open_hamburger_menu(self, driver):
        print("\n[TC-09] 햄버거 메뉴 열기")

        menu_btns = driver.find_elements(
            AppiumBy.XPATH,
            f'//android.widget.LinearLayout[@resource-id="{PKG}:id/top_right_menu"]'
            f'/android.widget.ImageButton'
        )

        assert len(menu_btns) > 0, "top_right_menu 안에 ImageButton이 없음"
        menu_btns[-1].click()
        print("  햄버거 버튼 클릭")
        time.sleep(1.5)

        sub_menu = wait_id(driver, "top_right_sub_menu", timeout=DEFAULT_TIMEOUT)
        assert sub_menu is not None, "서브메뉴(top_right_sub_menu)가 열리지 않음"
        print("  서브메뉴 노출 확인")

    def test_10_enter_settings(self, driver):
        print("\n[TC-10] 설정 화면 진입")

        setting_item = wait_text(driver, "설정", timeout=DEFAULT_TIMEOUT)
        assert setting_item is not None, "'설정' 항목을 찾을 수 없음"
        setting_item.click()
        print("  '설정' 클릭")
        time.sleep(1.5)

        logout_btn = wait_id(driver, "btn_logout", timeout=DEFAULT_TIMEOUT)
        assert logout_btn is not None, "설정 화면(btn_logout)이 표시되지 않음"
        print("  설정 화면 진입 확인")

    def test_11_click_logout(self, driver):
        print("\n[TC-11] 로그아웃 클릭")

        logout_btn = wait_id(driver, "btn_logout", timeout=DEFAULT_TIMEOUT)
        assert logout_btn is not None, "btn_logout 버튼을 찾을 수 없음"
        logout_btn.click()
        print("  로그아웃 버튼 클릭")
        time.sleep(2.0)

        confirm = wait_id(driver, "btn_alert_positive", timeout=5)
        if confirm:
            confirm.click()
            print("  로그아웃 확인 팝업 → 확인 클릭")
            time.sleep(2.0)

    def test_12_back_to_login_screen(self, driver):
        print("\n[TC-12] 로그인 화면 복귀 확인")

        loading = wait_id(driver, "layout_progress", timeout=5)
        if loading:
            print("  로딩 대기 중...")
            wait_gone(driver, "layout_progress")
            time.sleep(1.0)

        id_field = wait_id(driver, "et_id", timeout=DEFAULT_TIMEOUT)
        assert id_field is not None, "로그아웃 후 로그인 화면(et_id)으로 복귀 실패"
        print("  로그인 화면 복귀 확인")
        print("\nS01 시나리오 완료")
