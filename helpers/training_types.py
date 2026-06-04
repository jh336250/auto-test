"""
helpers/training_types.py
=========================
술술 읽기 훈련 유형 감지 및 처리 모듈.

[지원 유형]
  01. 소리 내어 읽기_색깔 읽기   → dropdown 조작 없이 layout_refresh_ui 대기
  02. 소리 내어 읽기_밑줄 읽기   → dropdown 조작 없이 layout_refresh_ui 대기
  03. 소리 내어 읽기_따라 읽기   → btn_complete 반복 클릭 → layout_refresh_ui
  04. 소리 내어 읽기_실감 읽기   → btn_record → 5초 → btn_complete → layout_refresh_ui
  05. 소리 내어 읽기_역할 읽기   → btn_complete 반복 클릭 → layout_refresh_ui
  06. 꼼꼼하게 읽기_끊어 읽기    → 이미지 매칭(first_06_point_1~4) → 탭
  07. 꼼꼼하게 읽기_문장 읽기    → 이미지 매칭(first_07_point) → 탭
  08. 꼼꼼하게 읽기_어휘 읽기    → 이미지 탭형 폴백(layout_refresh_ui 대기)
  09. 빠르게 읽기_훑어 읽기      → txt_timer 소멸 → dropdown 조작 없이 layout_refresh_ui
  10. 빠르게 읽기_쌩쌩 읽기      → dropdown 조작 없이 layout_refresh_ui 대기
  11. 속으로 읽기_누르며 읽기    → 이미지 매칭(first_11_point_1~3) → 탭 루프
  12. 속으로 읽기_짚으며 읽기    → 이미지 매칭(first_12_point) → 우측 드래그
  13. 표시하며 읽기              → btn_complete → popup_close → first_13_point 드래그
  14. 느끼면서 읽기              → btn_complete 반복 클릭 → layout_refresh_ui
  15. 반복하여 읽기              → btn_complete 반복 클릭 → layout_refresh_ui

[자세 확인 팝업 — LT-WS-200]
  android.widget.ImageButton(X 버튼) 클릭. 기본 3초 대기로 팝업 등장 감지.

[이미지 매칭]
  OpenCV 템플릿 매칭 (cv2.matchTemplate) 기반.
  img/ 디렉터리의 PNG 파일 사용.
  탭: mobile: clickGesture (W3C 호환, drv.tap() 대체)
"""

import os
import time

import numpy as np
import cv2

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

PKG              = "com.kyowon.literacy.store"
DEFAULT_TIMEOUT  = 15
TRAINING_TIMEOUT = 120
LOADING_TIMEOUT  = 60

IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "img")


# ──────────────────────────────────────────────────────────
# 내부 헬퍼 — Appium
# ──────────────────────────────────────────────────────────
def _wait_id(drv, resource_id, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, f"{PKG}:id/{resource_id}")
            )
        )
    except TimeoutException:
        return None


def _wait_id_clickable(drv, resource_id, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.ID, f"{PKG}:id/{resource_id}")
            )
        )
    except TimeoutException:
        return None


def _wait_text(drv, text, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(drv, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, f'//*[@text="{text}"]')
            )
        )
    except TimeoutException:
        return None


def _wait_gone(drv, resource_id, timeout=LOADING_TIMEOUT):
    try:
        WebDriverWait(drv, timeout).until_not(
            EC.presence_of_element_located(
                (AppiumBy.ID, f"{PKG}:id/{resource_id}")
            )
        )
    except TimeoutException:
        pass


def _find_id(drv, resource_id):
    try:
        return drv.find_element(AppiumBy.ID, f"{PKG}:id/{resource_id}")
    except NoSuchElementException:
        return None


# ──────────────────────────────────────────────────────────
# 내부 헬퍼 — OpenCV 이미지 매칭
# ──────────────────────────────────────────────────────────
def _screenshot_np(drv):
    png_bytes = drv.get_screenshot_as_png()
    arr = np.frombuffer(png_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _find_all_matches(drv, img_filename, threshold=0.83):
    img_path = os.path.join(IMG_DIR, img_filename)
    if not os.path.exists(img_path):
        print(f"  ⚠️ 이미지 파일 없음: {img_path}")
        return []
    screen   = _screenshot_np(drv)
    template = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if template is None:
        return []
    h, w = template.shape[:2]
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    locs = np.where(result >= threshold)
    matches = []
    for pt in zip(*locs[::-1]):
        cx, cy = pt[0] + w // 2, pt[1] + h // 2
        if not any(abs(cx - mx) < 30 and abs(cy - my) < 30 for mx, my in matches):
            matches.append((cx, cy))
    print(f"  ℹ️ [{img_filename}] 매칭: {len(matches)}개")
    return matches


def _find_best_match(drv, img_filename, threshold=0.60):
    img_path = os.path.join(IMG_DIR, img_filename)
    if not os.path.exists(img_path):
        print(f"  ⚠️ 이미지 파일 없음: {img_path}")
        return None
    screen   = _screenshot_np(drv)
    template = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if template is None:
        return None
    h, w = template.shape[:2]
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        print(f"  ℹ️ [{img_filename}] 매칭: ({cx},{cy}) score={max_val:.3f}")
        return (cx, cy)
    print(f"  ⚠️ [{img_filename}] 매칭 실패 (score={max_val:.3f})")
    return None


def _tap(drv, x, y):
    try:
        drv.execute_script("mobile: clickGesture", {"x": int(x), "y": int(y)})
    except Exception:
        from appium.webdriver.common.touch_action import TouchAction
        TouchAction(drv).tap(x=int(x), y=int(y)).perform()
    time.sleep(0.3)


def _drag_right(drv, sx, sy, distance=600):
    try:
        drv.execute_script(
            "mobile: dragGesture",
            {"startX": sx, "startY": sy,
             "endX": sx + distance, "endY": sy, "speed": 600}
        )
        print(f"  ✅ 드래그 ({sx},{sy}) → ({sx+distance},{sy})")
    except Exception as e:
        print(f"  ⚠️ 드래그 실패: {e}")
    time.sleep(0.5)


# ──────────────────────────────────────────────────────────
# 자세 확인 팝업 처리 (LT-WS-200)
# ──────────────────────────────────────────────────────────
def handle_posture_check(drv, wait=3):
    """
    바른자세 팝업 처리.

    중요:
      android.widget.ImageButton 클래스만으로는 바른자세 팝업 여부를 판단하지 않는다.
      훈련 화면의 지문보기/기타 버튼도 ImageButton일 수 있어 오클릭이 발생할 수 있기 때문이다.

    처리 기준:
      1. view_face_preview 또는 txt_check_fluency/notice_txt 존재 시에만 바른자세 팝업으로 판단
      2. 바른자세 팝업으로 확인된 경우에만 android.widget.ImageButton 클릭
      3. view_face_preview 소멸 확인
    """
    screen = _wait_id(drv, "view_face_preview", timeout=wait)
    status = _find_id(drv, "txt_check_fluency")
    notice = _find_id(drv, "notice_txt")

    # ImageButton 단독 감지는 금지: 지문보기(btn_expand) 등 일반 화면 버튼을 오클릭할 수 있음
    if not screen and not status and not notice:
        return False

    if status:
        print(f"  ℹ️ 바른자세 팝업 감지: [{status.text}]")
    else:
        print("  ℹ️ 바른자세 팝업 감지")

    try:
        image_buttons = WebDriverWait(drv, wait).until(
            EC.presence_of_all_elements_located(
                (AppiumBy.CLASS_NAME, "android.widget.ImageButton")
            )
        )
    except TimeoutException:
        image_buttons = []

    if not image_buttons:
        print("  ⚠️ 바른자세 팝업 X 버튼(android.widget.ImageButton) 미노출")
        return False

    try:
        image_buttons[0].click()
        print("  ✅ 바른자세 팝업 닫기(android.widget.ImageButton) 클릭")
        time.sleep(1.0)
    except Exception as e:
        print(f"  ⚠️ ImageButton 클릭 실패: {e}")
        return False

    _wait_gone(drv, "view_face_preview", timeout=10)
    print("  ✅ 바른자세 팝업 종료 확인")
    return True


# ──────────────────────────────────────────────────────────
# 훈련 가이드 팝업 처리 (훈련 화면 내)
# ──────────────────────────────────────────────────────────
def handle_training_guide_popup(drv):
    """
    훈련 화면 내 학습 가이드 팝업 처리.
    [dump 근거] dump_20260602_161656
      btn_skip_today 감지(3초) 시 btn_popup_close 클릭.
    """
    popup = _wait_id(drv, "btn_skip_today", timeout=3)
    if popup:
        close_btn = _wait_id_clickable(drv, "btn_popup_close", timeout=3)
        if close_btn:
            try:
                close_btn.click()
                print("  ✅ 훈련 가이드 팝업 닫기(btn_popup_close) 클릭")
                time.sleep(1.0)
                return True
            except Exception as e:
                print(f"  ⚠️ 훈련 가이드 팝업 닫기 실패: {e}")
    return False


# ──────────────────────────────────────────────────────────
# 공개 API
# ──────────────────────────────────────────────────────────
def detect_training_type(drv):
    """유형명 반환. 미감지 시 None."""
    el = _wait_id(drv, "txt_training_name", timeout=DEFAULT_TIMEOUT)
    if el:
        name = el.text.strip()
        print(f"  ℹ️ 훈련 유형 감지: [{name}]")
        return name
    print("  ⚠️ txt_training_name 미노출 → 훈련 유형 감지 실패")
    return None


def handle_training(drv):
    """
    훈련 유형 자동 감지 → 유형별 처리 → 지문보기 닫기.

    처리 순서:
      1. 훈련 가이드 팝업 (btn_skip_today + btn_popup_close)
      2. 자세 확인 팝업 (3초 대기 감지)
      3. txt_training_name 유형 감지 — 미감지 시 팝업 재확인 후 재시도
      4. 유형별 인터랙션
      5. btn_expand(지문보기) 닫기
    """
    handle_training_guide_popup(drv)
    handle_posture_check(drv, wait=3)
    name = detect_training_type(drv)
    if name is None:
        print("  ℹ️ 팝업 재확인 후 유형 재감지 시도...")
        handle_training_guide_popup(drv)
        handle_posture_check(drv, wait=3)
        name = detect_training_type(drv)
    if name is None:
        return None

    if any(k in name for k in ["색깔 읽기", "밑줄 읽기", "쌩쌩 읽기"]):
        _handle_speed(drv, name)
    elif "훑어 읽기" in name:
        _handle_skim(drv, name)
    elif any(k in name for k in ["따라 읽기", "역할 읽기", "느끼면서", "반복하여"]):
        _handle_complete_btn(drv, name)
    elif "실감 읽기" in name:
        _handle_recording(drv, name)
    elif "표시하며" in name:
        _handle_display_reading(drv, name)
    elif "끊어 읽기" in name:
        # 빗금(^) 전체 탭 — 스크롤 후 새 빗금이 나올 수 있어 루프 방식 사용
        _handle_image_tap_loop(drv, name,
            ["first_06_point_1.png", "first_06_point_2.png",
             "first_06_point_3.png", "first_06_point_4.png"])
    elif "문장 읽기" in name:
        _handle_image_tap(drv, name, ["first_07_point.png"])
    elif "누르며 읽기" in name:
        _handle_image_tap_loop(drv, name,
            ["first_11_point_1.png", "first_11_point_2.png", "first_11_point_3.png"])
    elif "짚으며 읽기" in name:
        _handle_image_drag_right(drv, name, "first_12_point.png")
    else:
        _handle_wait_complete(drv, name)

    _handle_expand_close(drv)
    return name


# ──────────────────────────────────────────────────────────
# 유형별 내부 처리
# ──────────────────────────────────────────────────────────
def _handle_speed(drv, name):
    """
    속도 선택형 처리.

    이번 자동화 코드에서는 dropdown 관련 확인/선택 기능을 사용하지 않음.
    resource-id: com.kyowon.literacy.store:id/dropdown 조작 삭제.
    화면이 자동 완료되는지 layout_refresh_ui만 대기함.
    """
    print(f"  ℹ️ [{name}] 처리: dropdown 조작 생략 → 완료 대기")
    _wait_for_complete(drv, name)


def _handle_skim(drv, name):
    """훑어 읽기: txt_timer 소멸 → dropdown 조작 없이 완료 대기."""
    print(f"  ℹ️ [{name}] 처리: 훑어 읽기(카운트다운 대기)")
    timer = _find_id(drv, "txt_timer")
    if timer:
        print("  ⏳ 카운트다운(txt_timer) 종료 대기...")
        _wait_gone(drv, "txt_timer", timeout=30)
        time.sleep(0.5)
    handle_posture_check(drv, wait=3)
    _wait_for_complete(drv, name)


def _handle_complete_btn(drv, name):
    """완료 버튼 반복 클릭형."""
    print(f"  ℹ️ [{name}] 처리: 완료 버튼 반복 클릭형")
    for attempt in range(30):
        handle_posture_check(drv, wait=1)
        if _find_id(drv, "layout_refresh_ui"):
            print(f"  ✅ [{name}] 훈련 완료 (layout_refresh_ui)")
            return
        complete = _wait_id_clickable(drv, "btn_complete", timeout=5)
        if complete:
            try:
                complete.click()
                print(f"  ✅ btn_complete 클릭 ({attempt+1}회)")
                time.sleep(1.0)
            except Exception as e:
                print(f"  ⚠️ btn_complete 클릭 실패: {e}")
        confirm = _find_id(drv, "btn_confirm")
        if confirm:
            confirm.click()
            print("  ✅ 확인 팝업(btn_confirm) 클릭")
            time.sleep(0.5)
        popup_close = _find_id(drv, "btn_popup_close")
        if popup_close:
            popup_close.click()
            print("  ✅ 팝업 닫기(btn_popup_close) 클릭")
            time.sleep(0.5)
        time.sleep(0.5)
    _wait_for_complete(drv, name)


def _handle_recording(drv, name):
    """실감 읽기: btn_record → 5초 → btn_complete."""
    print(f"  ℹ️ [{name}] 처리: 녹음형")
    rec = _wait_id_clickable(drv, "btn_record", timeout=40)
    if rec:
        rec.click()
        print("  ✅ 녹음(btn_record) 시작")
        time.sleep(5.0)
    complete = _wait_id_clickable(drv, "btn_complete", timeout=40)
    if complete:
        complete.click()
        print("  ✅ 녹음 완료(btn_complete) 클릭")
        time.sleep(1.0)
    _wait_for_complete(drv, name)


def _handle_display_reading(drv, name):
    """표시하며 읽기: btn_complete → popup_close → first_13_point 드래그."""
    print(f"  ℹ️ [{name}] 처리: 표시하며 읽기")
    complete = _wait_id_clickable(drv, "btn_complete", timeout=60)
    if complete:
        complete.click()
        print("  ✅ btn_complete 클릭")
        time.sleep(1.0)
        popup_close = _wait_id_clickable(drv, "btn_popup_close", timeout=5)
        if popup_close:
            popup_close.click()
            print("  ✅ 팝업 닫기(btn_popup_close) 클릭")
            time.sleep(0.5)
    pos = _find_best_match(drv, "first_13_point.png", threshold=0.60)
    if pos:
        _drag_right(drv, pos[0], pos[1])
    else:
        print("  ⚠️ first_13_point.png 매칭 실패 → 대기 폴백")
    _wait_for_complete(drv, name)


def _handle_image_tap(drv, name, img_files, threshold=0.83):
    """이미지 매칭 탭형 (끊어 읽기, 문장 읽기). mobile: clickGesture 사용."""
    print(f"  ℹ️ [{name}] 처리: 이미지 탭형")
    tapped = False
    for img_file in img_files:
        matches = _find_all_matches(drv, img_file, threshold=threshold)
        for (cx, cy) in matches:
            _tap(drv, cx, cy)
            print(f"  ✅ 탭: ({cx},{cy}) [{img_file}]")
            tapped = True
            time.sleep(0.3)
    if not tapped:
        print("  ⚠️ 이미지 매칭 없음 → 대기 폴백")
    _wait_for_complete(drv, name)


def _handle_image_tap_loop(drv, name, img_files):
    """이미지 매칭 탭 루프형 (누르며 읽기). mobile: clickGesture 사용."""
    print(f"  ℹ️ [{name}] 처리: 이미지 탭 루프형")
    for attempt in range(20):
        handle_posture_check(drv, wait=1)
        if _find_id(drv, "layout_refresh_ui"):
            print(f"  ✅ [{name}] 훈련 완료 ({attempt}회 루프)")
            return
        tapped = False
        for img_file in img_files:
            matches = _find_all_matches(drv, img_file, threshold=0.60)
            for (cx, cy) in matches:
                _tap(drv, cx, cy)
                print(f"  ✅ 탭: ({cx},{cy}) [{img_file}]")
                tapped = True
                time.sleep(0.3)
        if not tapped:
            time.sleep(1.5)
    _wait_for_complete(drv, name)


def _handle_image_drag_right(drv, name, img_file):
    """이미지 매칭 우측 드래그형 (짚으며 읽기)."""
    print(f"  ℹ️ [{name}] 처리: 이미지 우측 드래그형")
    pos = None
    for _ in range(15):
        pos = _find_best_match(drv, img_file, threshold=0.60)
        if pos:
            break
        time.sleep(2.0)
    if pos:
        _drag_right(drv, pos[0], pos[1])
    else:
        print(f"  ⚠️ {img_file} 매칭 실패 → 대기 폴백")
    _wait_for_complete(drv, name)


def _handle_wait_complete(drv, name):
    """폴백 — layout_refresh_ui 대기."""
    print(f"  ℹ️ [{name}] 처리: 폴백 (layout_refresh_ui 대기)")
    _wait_for_complete(drv, name)


def _wait_for_complete(drv, name):
    print(f"  ⏳ 훈련 완료 대기 (layout_refresh_ui, 최대 {TRAINING_TIMEOUT}초)...")
    result = _wait_id(drv, "layout_refresh_ui", timeout=TRAINING_TIMEOUT)
    if result:
        print(f"  ✅ [{name}] 훈련 완료 확인 (layout_refresh_ui)")
    else:
        print(f"  ⚠️ [{name}] layout_refresh_ui 미노출 (타임아웃)")


def _handle_expand_close(drv):
    """지문보기(btn_expand) 열기 → 닫기."""
    expand = _find_id(drv, "btn_expand")
    if expand:
        try:
            expand.click()
            print("  ✅ 지문보기(btn_expand) 클릭")
            time.sleep(0.5)
            close = _wait_id_clickable(drv, "btn_popup_close", timeout=5)
            if close:
                close.click()
                print("  ✅ 지문보기 닫기(btn_popup_close) 클릭")
                time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️ 지문보기 처리 실패: {e}")
