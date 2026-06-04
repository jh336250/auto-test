# =================================================
# QA 자동화 스크립트 - 문해력 술술 읽기 훈련 기능 함수 스크립트
# 👤 Author: Eden Kim
# 📅 Date: 2026-01-22 - v1.0.5
#   - 술술 읽기 훈련 기능 추가: 훈련 15종 감지 및 기능 수행
#   - 독서 활동 기능 추가: 활동형 7종, 문제형 11종 감지 및 기능 수행
#   - 어휘 탐험 기능 추가: 어휘 나무, 일반 영상, 어휘 카드/한 컷 툰 감지 및 기능 수행
#   - 어휘 놀이 기능 추가: 드래그형 1종, 보기 선택형 1종 감지 및 기능 수행
#   - 오류 방지를 위해 .get_text()를 get_label()로 대체
# =================================================
# -*- encoding=utf8 -*-
__author__ = "Owner"

import os, sys, random, re, time

# 이 스크립트가 있는 .air 폴더 경로
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

# 여기를 파이썬 모듈 탐색 경로에 강제로 올린다
if CUR_DIR not in sys.path:
    sys.path.insert(0, CUR_DIR)

# QA_TOOLKIT도 있으면 같이 올린다
TOOLKIT = os.getenv("QA_TOOLKIT")
if TOOLKIT and TOOLKIT not in sys.path:
    sys.path.insert(0, TOOLKIT)

from airtest.core.api import *
from literacy_test import *
from common import *
from common import _get_resolution, _get_region_from_poco

# ----- step_block: 술술 읽기 훈련 공통 함수(일반 호출로도 사용 가능)
def first_training_func():
    handle_exceptions()
    # 복습 시 재시작
    if poco("com.kyowon.literacy:id/btnRetry").exists():
        step("다시 하기 버튼 감지 → 학습 재시작")
        must_click(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 클릭")
        time.sleep(2.0)
    
    # 01_소리 내어 읽기_색깔 읽기
    if poco("com.kyowon.literacy:id/txt_training_name", text="소리 내어 읽기_색깔 읽기").exists():
        step("소리 내어 읽기_색깔 읽기 감지됨 🔍")
        must_click(poco("com.kyowon.literacy:id/layout_spinner").offspring("com.kyowon.literacy:id/dropdown"), "속도 선택 클릭")
        must_click(poco("com.kyowon.literacy:id/recycler").child(text="더 빠르게"), "더 빠르게 클릭")
        time.sleep(20)
        handle_exceptions()
        must_check(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 확인", timeout=100)
        step("소리 내어 읽기_색깔 읽기 완료 ✔️")

    # 02_소리 내어 읽기_밑줄 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="소리 내어 읽기_밑줄 읽기").exists():
        step("소리 내어 읽기_밑줄 읽기 감지됨 🔍")
        must_click(poco("com.kyowon.literacy:id/layout_spinner").offspring("com.kyowon.literacy:id/dropdown"), "속도 선택 클릭")
        must_click(poco("com.kyowon.literacy:id/recycler").child(text="더 빠르게"), "더 빠르게 클릭")
        time.sleep(20)
        handle_exceptions()
        must_check(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 확인", timeout=100)
        step("소리 내어 읽기_밑줄 읽기 완료 ✔️")

    # 03_소리 내어 읽기_따라 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="소리 내어 읽기_따라 읽기").exists():
        step("소리 내어 읽기_따라 읽기 감지됨 🔍")
        def first_03_func():
            if try_check(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete", enabled=True), "완료 버튼 활성화 감지", timeout=60):
                must_click(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 클릭")
        repeat_action_until_exists(poco("com.kyowon.literacy:id/btnRetry"), first_03_func)
        step("소리 내어 읽기_따라 읽기 완료 ✔️")

    # 04_소리 내어 읽기_실감 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="소리 내어 읽기_실감 읽기").exists():
        step("소리 내어 읽기_실감 읽기 감지됨 🔍")
        if try_check(poco("com.kyowon.literacy:id/btn_record"), "녹음 버튼 감지", timeout=40):
            must_click(poco("com.kyowon.literacy:id/btn_record"), "녹음 버튼 클릭")
            time.sleep(5.0)  # 녹음 시간 대기
            if try_check(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 감지", timeout=40):
                must_click(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 클릭")
            must_check(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 확인", timeout=60)
        step("소리 내어 읽기_실감 읽기 완료 ✔️")

    # 05_소리 내어 읽기_역할 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="소리 내어 읽기_역할 읽기").exists():
        step("소리 내어 읽기_역할 읽기 감지됨 🔍")
        def first_05_func():
            if try_check(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 감지", timeout=40):
                must_click(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 클릭")
        repeat_action_until_exists(poco("com.kyowon.literacy:id/btnRetry"), first_05_func)
        step("소리 내어 읽기_역할 읽기 완료 ✔️")

    # 06_꼼꼼하게 읽기_끊어 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="꼼꼼하게 읽기_끊어 읽기").exists():
        step("꼼꼼하게 읽기_끊어 읽기 감지됨 🔍")
        layer = poco("com.kyowon.literacy:id/layout_content")
        if exists(Template(r"first_06_point_1.png", threshold=0.83, rgb=True)):
            step("포인트(핫도그) 감지 → 연속 터치 진행")
            cnt = tap_images(
                img_path=r"first_06_point_1.png",
                layer_poco=layer,
                debug=False,
            )
        if exists(Template(r"first_06_point_2.png", threshold=0.83, rgb=True)):
            step("포인트(지팡이) 감지 → 연속 터치 진행")
            cnt = tap_images(
                img_path=r"first_06_point_2.png",
                layer_poco=layer,
                debug=False,
            )
        if exists(Template(r"first_06_point_3.png", threshold=0.83, rgb=True)):
            step("포인트(당근) 감지 → 연속 터치 진행")
            cnt = tap_images(
                img_path=r"first_06_point_3.png",
                layer_poco=layer,
                debug=False,
            )
        if exists(Template(r"first_06_point_4.png", threshold=0.83, rgb=True)):
            step("포인트(우산) 감지 → 연속 터치 진행")
            cnt = tap_images(
                img_path=r"first_06_point_4.png",
                layer_poco=layer,
                debug=False,
            )
        step("꼼꼼하게 읽기_끊어 읽기 완료 ✔️")

    # 07_꼼꼼하게 읽기_문장 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="꼼꼼하게 읽기_문장 읽기").exists():
        step("꼼꼼하게 읽기_문장 읽기 감지됨 🔍")
        layer = poco("com.kyowon.literacy:id/layout_content")
        if exists(Template(r"first_07_point.png", threshold=0.83, rgb=True)):
            step("포인트 감지 → 연속 터치 진행")
            tap_images(
                img_path=r"first_07_point.png",
                layer_poco=layer,
                threshold=0.90,
                color_mean_abs_max=10,
                color_pixel_diff_max=20,
                color_ratio_min=0.94,
                debug=False,
            )
        step("꼼꼼하게 읽기_문장 읽기 완료 ✔️")

    # 08_꼼꼼하게 읽기_어휘 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="꼼꼼하게 읽기_어휘 읽기").exists():
        step("꼼꼼하게 읽기_어휘 읽기 감지됨 🔍")
        layer = poco("com.kyowon.literacy:id/layout_content").offspring("com.kyowon.literacy:id/txt_content")
        def close_popup():
            # 너희 common의 click_core / safe_click / poco click 등을 쓰면 됨
            must_click(poco("com.kyowon.literacy:id/btn_popup_close"), "팝업 닫기 클릭")

        tap_color_words(
            layer_poco=layer,
            verify_fn=lambda: poco("com.kyowon.literacy:id/btn_popup_close").exists(),
            popup_close_fn=close_popup,
            debug=False,
        )
        step(f"꼼꼼하게 읽기_어휘 읽기 완료 ✔️")

    # 09_빠르게 읽기_훑어 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="빠르게 읽기_훑어 읽기").exists():
        step("빠르게 읽기_훑어 읽기 감지됨 🔍")
        if try_check(poco("com.kyowon.literacy:id/txt_timer"), "타이머 확인 → 카운트 다운까지 대기"):
            poco("com.kyowon.literacy:id/txt_timer").wait_for_disappearance(timeout=30)
        must_click(poco("com.kyowon.literacy:id/layout_spinner").offspring("com.kyowon.literacy:id/dropdown"), "속도 선택 클릭")
        must_click(poco("com.kyowon.literacy:id/recycler").child(text="더 빠르게"), "더 빠르게 클릭")
        time.sleep(20)
        handle_exceptions()
        must_check(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 확인", timeout=100)
        step("빠르게 읽기_훑어 읽기 완료 ✔️")

    # 10_빠르게 읽기_쌩쌩 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="빠르게 읽기_쌩쌩 읽기").exists():
        step("빠르게 읽기_쌩쌩 읽기 감지됨 🔍")
        must_click(poco("com.kyowon.literacy:id/layout_spinner").offspring("com.kyowon.literacy:id/dropdown"), "속도 선택 클릭")
        must_click(poco("com.kyowon.literacy:id/recycler").child(text="더 빠르게"), "더 빠르게 클릭")
        time.sleep(20)
        handle_exceptions()
        must_check(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 확인", timeout=100)
        step("빠르게 읽기_쌩쌩 읽기 완료 ✔️")

    # 11_속으로 읽기_누르며 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="속으로 읽기_누르며 읽기").exists():
        step("속으로 읽기_누르며 읽기 감지됨 🔍")
        handle_exceptions()
        def first_11_func():
            if try_check(poco("com.kyowon.literacy:id/layout_content").offspring("com.kyowon.literacy:id/frameLayout").child("android.view.View"), "내용 확인", timeout=30):
                if exists(Template(r"first_11_point_1.png")):
                    step("포인트(별) 감지 → 터치 진행")
                    tap_images(r"first_11_point_1.png", rgb=False, color_gate=False)
                if exists(Template(r"first_11_point_2.png")):
                    step("포인트(클로버) 감지 → 터치 진행")
                    tap_images(r"first_11_point_2.png", rgb=False, color_gate=False)
                if exists(Template(r"first_11_point_3.png")):
                    step("포인트(우주선) 감지 → 터치 진행")
                    tap_images(r"first_11_point_3.png", rgb=False, color_gate=False)
        repeat_action_until_exists(poco("com.kyowon.literacy:id/btnRetry"), first_11_func)
        step("속으로 읽기_누르며 읽기 완료 ✔️")

    # 12_속으로 읽기_짚으며 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="속으로 읽기_짚으며 읽기").exists():
        step("속으로 읽기_짚으며 읽기 감지됨 🔍")
        handle_exceptions()
        target = r"first_12_point.png"
        wait(Template(target, threshold=0.82), timeout=30.0)
        # target = poco("com.kyowon.literacy:id/layout_content").offspring("com.kyowon.literacy:id/frameLayout").child("android.widget.ImageView")
        # target.wait_for_appearance(timeout=30.0)
        step("타겟 발견 드래그 시도")
        layer = poco("com.kyowon.literacy:id/layout_content").offspring("com.kyowon.literacy:id/scrollview")
        drag_right_from_target(
            target=target,
            layer_poco=layer,
            done_poco=poco("com.kyowon.literacy:id/btnRetry"),  # 또는 btn_refresh
            debug=False,
        )
        step("속으로 읽기_짚으며 읽기 완료 ✔️")

    # 13_표시하며 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="표시하며 읽기").exists():
        step("표시하며 읽기 감지됨 🔍")
        if try_check(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete", enabled=True), "완료 버튼 활성화 감지", timeout=60):
            must_click(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 클릭")
            must_click(poco("com.kyowon.literacy:id/btn_popup_close"), "팝업 닫기 클릭")
            layer = poco("com.kyowon.literacy:id/contentRoot")
            target = r"first_13_point.png"
            drag_right_from_target(
                target=target,
                layer_poco=layer,
                done_poco=poco("com.kyowon.literacy:id/btnRetry"),  # 또는 btn_refresh
                debug=False,
            )
            step("표시하며 읽기 완료 ✔️")

    # 14_느끼면서 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="느끼면서 읽기").exists():
        step("느끼면서 읽기 감지됨 🔍")
        def first_14_func():
            if try_check(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 감지", timeout=40):
                must_click(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 클릭")
                time.sleep(0.5)
                if poco("com.kyowon.literacy:id/btn_confirm").exists():
                    must_click(poco("com.kyowon.literacy:id/btn_confirm"), "팝업 확인 클릭")
        repeat_action_until_exists(poco("com.kyowon.literacy:id/btnRetry"), first_14_func)
        step("느끼면서 읽기 완료 ✔️")

    # 15_반복하여 읽기
    elif poco("com.kyowon.literacy:id/txt_training_name", text="반복하여 읽기").exists():
        step("반복하여 읽기 감지됨 🔍")
        def first_15_func():
            if try_check(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 감지", timeout=40):
                must_click(poco("com.kyowon.literacy:id/layout_attach_ui").offspring("com.kyowon.literacy:id/btn_complete"), "완료 버튼 클릭")
                time.sleep(0.5)
                if poco("com.kyowon.literacy:id/btn_popup_close").exists():
                    must_click(poco("com.kyowon.literacy:id/btn_popup_close"), "팝업 닫기 클릭")
        repeat_action_until_exists(poco("com.kyowon.literacy:id/btnRetry"), first_15_func)
        step("반복하여 읽기 완료 ✔️")

    # 유형 미감지
    else:
        handled = handle_exceptions()
        if handled > 0:
            step(f"예외 처리 완료: {handled}건")
            return
        soft_fail("술술 읽기 훈련 유형 미감지: FAIL ❌ - 어떤 유형도 감지되지 않음")
        raise RuntimeError("[ERR] 술술 읽기 훈련 유형 미감지 - 조건 불일치(루프 종료)")

    must_click(poco("com.kyowon.literacy:id/btn_expand"), "지문보기 클릭")
    must_click(poco("com.kyowon.literacy:id/btn_popup_close"), "지문보기 닫기")

# ----- step_block: 독서 활동 공통 함수(일반 호출로도 사용 가능)
def first_reading_act_func():
    handle_exceptions()
    while(True):
        time.sleep(1.0)

        # 진행률 체크
        if poco("com.kyowon.literacy:id/progressText", text="8/8") and poco("com.kyowon.literacy:id/btnRetry").exists():
            step("진행률 8/8 도달")
            break

        # 복습 확인
        if poco("com.kyowon.literacy:id/btnRetry").exists():
            step("다시 하기 버튼 감지 → 활동 재시작")
            must_click(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 클릭")
            time.sleep(1.0)

        # 활동형_드래그 판별
        if poco("com.kyowon.literacy:id/dropTarget").exists():
            # 활동형_드래그1
            if poco("com.kyowon.literacy:id/dragItemArea").exists():
                step("활동형_드래그1 감지 🔍")
                answers = poco("com.kyowon.literacy:id/dragItemArea").children()
                target = poco("com.kyowon.literacy:id/dropTarget")
                for answer in answers:
                    label = get_label(answer.offspring('com.kyowon.literacy:id/selectionText'))
                    must_drag(answer, target, f"보기 선택({label})")
                    time.sleep(5.0)
                    if poco(text="정답 및 풀이").exists():
                        step(f"{label}: 정답 ✅")
                        must_click(poco("com.kyowon.literacy:id/exitButton"), "정답 및 풀이 팝업 닫기")
                        if poco("com.kyowon.literacy:id/nextButton").exists():
                            must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
                        break
                    else:
                        step(f"{label}: 오답 ⚠️")
                else:
                    soft_fail("활동형_드래그1: FAIL ❌ - 정답 및 풀이 화면 미노출")
                    raise RuntimeError("[ERR] 활동형_드래그1 실패 - 정답 및 풀이 화면 미노출")
                continue

            # 활동형_드래그2
            elif poco("com.kyowon.literacy:id/selectionGroup").offspring("com.kyowon.literacy:id/dragTarget").exists():
                step("활동형_드래그2 감지 🔍")
                answers = poco("com.kyowon.literacy:id/selectionGroup").children()
                target = poco("com.kyowon.literacy:id/dropTarget")
                for answer in answers:
                    label_obj = answer.offspring("com.kyowon.literacy:id/myTextView")
                    if not label_obj.exists():
                        label_obj = answer.offspring("com.kyowon.literacy:id/textView")

                    label = get_label(label_obj) if label_obj.exists() else ""
                    must_drag(
                        answer,
                        target,
                        f"보기 선택({label})",
                        src_offset=(400, 0)
                    )
                    time.sleep(5.0)
                    if poco(text="정답 및 풀이").exists():
                        step(f"{label}: 정답 ✅")
                        must_click(poco("com.kyowon.literacy:id/exitButton"), "정답 및 풀이 팝업 닫기")
                        if poco("com.kyowon.literacy:id/nextButton").exists():
                            must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
                        break
                    else:
                        step(f"{label}: 오답 ⚠️")
                else:
                    soft_fail("활동형_드래그2: FAIL ❌ - 정답 및 풀이 화면 미노출")
                    raise RuntimeError("[ERR] 활동형_드래그2 실패 - 정답 및 풀이 화면 미노출")
                continue

            # 활동형_드래그3
            elif poco("com.kyowon.literacy:id/coinFrame").exists():
                step("활동형_드래그3 감지 🔍")
                answers = poco("com.kyowon.literacy:id/selectionGroup").children()
                target = poco("com.kyowon.literacy:id/dropTarget")
                for answer in answers:
                    label = get_label(answer.offspring("com.kyowon.literacy:id/selectionText"))
                    must_drag(answer, target, f"보기 선택({label})")
                    time.sleep(5.0)
                    if poco(text="정답 및 풀이").exists():
                        step(f"{label}: 정답 ✅")
                        must_click(poco("com.kyowon.literacy:id/exitButton"), "정답 및 풀이 팝업 닫기")
                        if poco("com.kyowon.literacy:id/nextButton").exists():
                            must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
                        break
                    else:
                        step(f"{label}: 오답 ⚠️")
                else:
                    soft_fail("활동형_드래그3: FAIL ❌ - 정답 및 풀이 화면 미노출")
                    raise RuntimeError("[ERR] 활동형_드래그3 실패 - 정답 및 풀이 화면 미노출")
                continue
            
            # 활동형_드래그 유형 미감지
            else:
                handled = handle_exceptions()
                if handled > 0:
                    step(f"예외 처리 완료: {handled}건")
                    continue
                soft_fail(f"활동형_드래그 유형 미감지({get_label(poco('com.kyowon.literacy:id/progressText'))}): FAIL ❌ - 어떤 유형도 감지되지 않음")
                raise RuntimeError("[ERR] 활동형_드래그 유형 미감지 - 조건 불일치(루프 종료)")

        # 활동형_O/X
        elif poco("com.kyowon.literacy:id/oButton").exists():
            step("활동형_O/X 감지 🔍")
            for btn_id, label in [
                ("com.kyowon.literacy:id/oButton", "보기 O"),
                ("com.kyowon.literacy:id/xButton", "보기 X"),
            ]:
                must_click(poco(btn_id), f"{label} 클릭")
                time.sleep(5.0)

                if poco(text="정답 및 풀이").exists():
                    step(f"{label}: 정답 ✅")
                    must_click(poco("com.kyowon.literacy:id/exitButton"), "정답 및 풀이 팝업 닫기")
                    if poco("com.kyowon.literacy:id/nextButton").exists():
                        must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
                    break
                else:
                    step(f"{label}: 오답 ⚠️")
            else:
                soft_fail("활동형_O/X: FAIL ❌ - 정답 및 풀이 화면 미노출")
                raise RuntimeError("[ERR] 활동형_O/X 실패 - 정답 및 풀이 화면 미노출")
            continue
        
        # 활동형_보기 선택
        elif poco("com.kyowon.literacy:id/answerArea").exists():
            step("활동형_보기 선택 감지 🔍")
            answers = poco("com.kyowon.literacy:id/answerArea").children()
            for answer in answers:
                label = get_label(answer.offspring("com.kyowon.literacy:id/itemText"))
                must_click(answer, f"보기 선택({label})")
                time.sleep(5.0)
                if poco(text="정답 및 풀이").exists():
                    step(f"{label}: 정답 ✅")
                    must_click(poco("com.kyowon.literacy:id/exitButton"), "정답 및 풀이 팝업 닫기")
                    if poco("com.kyowon.literacy:id/nextButton").exists():
                        must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
                    break
                else:
                    step(f"{label}: 오답 ⚠️")
            else:
                soft_fail("활동형_보기 선택: FAIL ❌ - 정답 및 풀이 화면 미노출")
                raise RuntimeError("[ERR] 활동형_보기 선택 실패 - 정답 및 풀이 화면 미노출")
            continue

        # 활동형_보기 선택2
        elif poco("com.kyowon.literacy:id/selectionGroup").offspring('com.kyowon.literacy:id/selectionText').exists():
            step("활동형_보기 선택2 감지 🔍")
            answers = poco("com.kyowon.literacy:id/selectionGroup").children()
            for answer in answers:
                label = get_label(answer.offspring("com.kyowon.literacy:id/selectionText"))
                must_click(answer, f"보기 선택({label})")
                time.sleep(5.0)
                if poco(text="정답 및 풀이").exists():
                    step(f"{label}: 정답 ✅")
                    must_click(poco("com.kyowon.literacy:id/exitButton"), "정답 및 풀이 팝업 닫기")
                    if poco("com.kyowon.literacy:id/nextButton").exists():
                        must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
                    break
                else:
                    step(f"{label}: 오답 ⚠️")
            else:
                soft_fail("활동형_보기 선택2: FAIL ❌ - 정답 및 풀이 화면 미노출")
                raise RuntimeError("[ERR] 활동형_보기 선택2 실패 - 정답 및 풀이 화면 미노출")
            continue
            
        # 활동형_선긋기
        elif poco("com.kyowon.literacy:id/lineDrawView").exists():
            step("활동형_선긋기 감지 🔍")

            top_answers = list(poco("com.kyowon.literacy:id/toplayout").children())
            bottom_answers = list(poco("com.kyowon.literacy:id/bottomlayout").children())

            # 방어: 비어있는 경우
            if not top_answers or not bottom_answers:
                soft_fail("활동형_선긋기: FAIL ❌ - 매칭 대상이 비어있음")
                raise RuntimeError("[ERR] 활동형_선긋기 실패 - 매칭 대상 비어있음")

            # top을 순서대로 처리하면서, 각 top에 대해 남은 bottom 후보를 순서대로 시도
            for ti, top_answer in enumerate(top_answers):
                top_dot = top_answer.offspring("com.kyowon.literacy:id/bottom_dot_1")
                top_txt_obj = top_answer.offspring("com.kyowon.literacy:id/moletext")
                top_txt = get_label(top_txt_obj) if top_txt_obj.exists() else f"TOP[{ti}]"

                matched = False

                # bottom 후보가 소진되면 실패
                if not bottom_answers:
                    soft_fail("활동형_선긋기: FAIL ❌ - bottom 후보 소진")
                    raise RuntimeError("[ERR] 활동형_선긋기 실패 - bottom 후보 소진")

                # 현재 top에 대해 bottom을 하나씩 찍어보며 ROI 변화로 성공 판정
                for bi, bottom_answer in enumerate(list(bottom_answers)):  # 원본 제거를 위해 복사본 순회
                    bottom_dot = bottom_answer.offspring("com.kyowon.literacy:id/top_dot_1")
                    bottom_txt_obj = bottom_answer.offspring("com.kyowon.literacy:id/moletext")
                    bottom_txt = get_label(bottom_txt_obj) if bottom_txt_obj.exists() else f"BOT[{bi}]"

                    desc = f"답변 드래그: {top_txt} - {bottom_txt}"

                    ok = try_drag_with_roi(
                        top_dot,
                        bottom_dot,
                        desc,
                        debug=False,
                    )

                    if ok:
                        # ✅ 매칭 성공: 해당 bottom을 후보에서 제거하고 다음 top으로
                        bottom_answers.remove(bottom_answer)
                        matched = True
                        step(f"매칭 성공 ✅ : {top_txt} -> {bottom_txt}", False)
                        break
                    else:
                        step(f"매칭 실패 → 다음 후보 시도: {top_txt} -> {bottom_txt}", False)

                if not matched:
                    step(f"활동형_선긋기: FAIL ❌ - 매칭 실패(top[{ti}]={top_txt})")
                    raise RuntimeError(f"[ERR] 활동형_선긋기 실패 - top[{ti}] 매칭 불가")

            # ✅ 모든 매칭이 끝난 뒤 정답/풀이 팝업 확인
            time.sleep(1.0)
            if try_check(poco(text="정답 및 풀이"), "정답 및 풀이 화면 확인", timeout=5):
                must_click(poco("com.kyowon.literacy:id/exitButton"), "종료 버튼 클릭")
                if poco("com.kyowon.literacy:id/nextButton").exists():
                    must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
            else:
                soft_fail("활동형_선긋기: FAIL ❌ - 전체 매칭 후 정답 및 풀이 화면 미노출")
                raise RuntimeError("[ERR] 활동형_선긋기 실패 - 전체 매칭 후 정답 및 풀이 화면 미노출")

            continue


        # 문제형 공통 처리 로직 시작
        elif (poco("com.kyowon.literacy:id/questionText").exists() or poco("com.kyowon.literacy:id/question_txt").exists()):
            step("문제형 감지 🔍")
            must_drag(
                poco("com.kyowon.literacy:id/layout_bottom_ui"), 
                poco("com.kyowon.literacy:id/layout_learning_topbar"), 
                "스크롤 업 드래그",
                src_offset=(-800, 0),
                dst_offset=(-800, 0)
            )
            time.sleep(1.0)

            # O/X 문제
            if poco("com.kyowon.literacy:id/radio_group").exists():
                step("O/X 문제 감지 🔍")
                answers = poco("com.kyowon.literacy:id/content_panel").children().child("com.kyowon.literacy:id/radio_group")
                for answer in answers:
                    selectors = list(answer.children())
                    selector = random.choice(selectors) if selectors else None
                    if selector:
                        must_click(selector, f"O/X 버튼 클릭: {selector.get_name()}")
                    else:
                        soft_fail("O/X 문제: FAIL ❌ - 선택지 미노출")

            # 매칭형 문제
            elif poco("com.kyowon.literacy:id/answer_panel_top").exists():
                step("매칭형 문제 감지 🔍")
                top_answers = poco("com.kyowon.literacy:id/answer_panel_top").children()
                bottom_answers = list(poco("com.kyowon.literacy:id/answer_panel_bottom").children())
                target = None
                for top_answer in top_answers:
                    target = bottom_answers.pop(random.randrange(len(bottom_answers)) if bottom_answers else None)
                    must_drag(
                        top_answer.offspring("android.widget.ImageView"), 
                        target.offspring("android.widget.ImageView"), 
                        f"답변 드래그: {get_label(top_answer.child('com.kyowon.literacy:id/point_view_txt'))} - {get_label(target.child('com.kyowon.literacy:id/point_view_txt'))}",
                        debug=False
                    )
                    time.sleep(1.0)

            # 패널 선택형 문제
            elif poco("com.kyowon.literacy:id/clickable_panel").exists():
                step("패널 선택형 문제 감지 🔍")
                answers = poco("com.kyowon.literacy:id/answer_panel").children().child("com.kyowon.literacy:id/clickable_panel")
                answer = random.choice(answers) if answers else None
                if answer:
                    must_click(answer, f"랜덤 패널 클릭: {get_label(answer.offspring('com.kyowon.literacy:id/answer_txt'))}")
                else:
                    soft_fail("패널 선택형 문제: FAIL ❌ - 선택지 미노출")

            # 보기 선택형 문제
            elif poco("com.kyowon.literacy:id/descframe").exists():
                step("보기 선택형 문제 감지 🔍")
                answers = poco("com.kyowon.literacy:id/selectiongroup").children().offspring("com.kyowon.literacy:id/descframe")
                answer = random.choice(answers) if answers else None
                if answer:
                    must_click(answer, f"랜덤 보기 클릭: {get_label(answer.offspring('com.kyowon.literacy:id/selectiondesc'))}")
                else:
                    soft_fail("보기 선택형 문제: FAIL ❌ - 선택지 미노출")
                
            # 퀴즈 선택형 문제
            elif poco("com.kyowon.literacy:id/quiz_select_button").exists():
                step("퀴즈 선택형 문제 감지 🔍")
                answers = poco("com.kyowon.literacy:id/answer_panel").children()
                answer = random.choice(answers) if answers else None
                if answer:
                    must_click(answer.child("com.kyowon.literacy:id/quiz_select_button"), f"랜덤 보기 클릭: {get_label(answer.offspring('com.kyowon.literacy:id/quiz_txt'))}")
                else:
                    soft_fail("퀴즈 선택형 문제: FAIL ❌ - 선택지 미노출")

            # 다중 보기 드래그 문제
            elif poco("com.kyowon.literacy:id/drag_txt").exists():
                step("다중 보기 드래그 문제 감지 🔍")
                step("드롭 포인트 탐색 어려움으로 스킵 처리 ⏩")

            # 항목 별 OX 문제
            elif poco("com.kyowon.literacy:id/question_spinner_outer").exists():
                step("항목 별 OX 문제 감지 🔍")
                answers = poco("com.kyowon.literacy:id/answer_panel").children()
                for answer in answers:
                    must_click(
                        answer.child("com.kyowon.literacy:id/question_spinner_outer"), 
                        f"항목 선택({get_label(answer.offspring('com.kyowon.literacy:id/question_txt'))})"
                    )
                    selectors = poco("com.kyowon.literacy:id/answer_select_panel").children()
                    selector = random.choice(selectors) if selectors else None
                    if selector:
                        must_click(selector, f"O/X 선택({get_label(selector.offspring('com.kyowon.literacy:id/question_spinner_item'))})")
                    time.sleep(1.0)

            # 보기 상자 드래그 문제
            elif poco("com.kyowon.literacy:id/questionImage").exists():
                step("보기 상자 드래그 문제 감지 🔍")

                answers = poco("com.kyowon.literacy:id/selectiongroup").children()
                answer = random.choice(answers) if answers else None

                target = poco("com.kyowon.literacy:id/questionImage")

                must_drag(answer, target, "랜덤 상자 드래그")

            # 이미지 2개 선택형 문제
            elif poco("com.kyowon.literacy:id/selectionframe").exists():
                step("이미지 2개 선택형 문제 감지 🔍")
                answers = list(poco("com.kyowon.literacy:id/selectiongroup").children())
                answer = answers.pop(random.randrange(len(answers))) if answers else None
                
                if answer:
                    must_click(answer.offspring("android.widget.FrameLayout"), f"랜덤 보기 클릭: {get_label(answer.offspring('com.kyowon.literacy:id/selectionimage'))}")
                else:
                    soft_fail("이미지 2개 선택형 문제: FAIL ❌ - 선택지 미노출")
                
                answer2 = answers.pop(random.randrange(len(answers))) if answers else None

                if answer2:
                    must_click(answer2.offspring("android.widget.FrameLayout"), f"랜덤 보기 클릭: {get_label(answer2.offspring('com.kyowon.literacy:id/selectionimage'))}")
                else:
                    soft_fail("이미지 2개 선택형 문제: FAIL ❌ - 선택지 미노출")

            # 선긋기 문제
            elif poco("com.kyowon.literacy:id/point_view_left").exists():
                step("선긋기 문제 감지 🔍")
                left_targets = poco("com.kyowon.literacy:id/answer_panel").children().child("com.kyowon.literacy:id/point_view_left")
                right_targets = list(poco("com.kyowon.literacy:id/answer_panel").children().child("com.kyowon.literacy:id/point_view_right"))
                right_target = None
                for left_target in left_targets:
                    right_target = right_targets.pop(random.randrange(len(right_targets)) if right_targets else None)
                    must_drag(
                        left_target, 
                        right_target, 
                        f"답변 드래그: {left_target} - {get_label(right_target.parent().child('com.kyowon.literacy:id/point_view_txt'))}",
                        debug=False,
                    )
                    time.sleep(1.0)

            # 텍스트 입력 문제
            elif poco("com.kyowon.literacy:id/answer_input_panel").exists():
                step("텍스트 입력 문제 감지 🔍")
                must_type(poco("com.kyowon.literacy:id/answer_edit1"), "홍길동", "글자 입력: 홍길동")

            # 문제형 유형 미감지
            else:
                handled = handle_exceptions()
                if handled > 0:
                    step(f"예외 처리 완료: {handled}건")
                    continue
                soft_fail(f"문제형 유형 미감지({get_label(poco('com.kyowon.literacy:id/progressText'))}): FAIL ❌ - 어떤 유형도 감지되지 않음")
                raise RuntimeError("[ERR] 문제형 유형 미감지 - 조건 불일치(루프 종료)")

            time.sleep(0.5)
            must_click(poco("com.kyowon.literacy:id/markButton"), "채점하기 클릭")
            if poco("com.kyowon.literacy:id/btn_alert_positive").exists():
                must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "확인 버튼 클릭")
            if poco("com.kyowon.literacy:id/nextButton").exists():
                must_click(poco("com.kyowon.literacy:id/nextButton"), "다음 버튼 클릭")
            continue
        
        # 독서 활동 유형 미감지
        else:
            handled = handle_exceptions()
            if handled > 0:
                step(f"예외 처리 완료: {handled}건")
                continue
            soft_fail(f"독서 활동 유형 미감지({get_label(poco('com.kyowon.literacy:id/progressText'))}): FAIL ❌ - 어떤 유형도 감지되지 않음")
            raise RuntimeError("[ERR] 독서 활동 유형 미감지 - 조건 불일치(루프 종료)")

# ----- step_block: 어휘 탐험 공통 함수(일반 호출로도 사용 가능)
def first_voca_adv_func():
    handle_exceptions()

    # 다시 하기 버튼 발견 시 재시작
    if poco("com.kyowon.literacy:id/btnRetry").exists():
        step("다시 하기 버튼 감지 → 학습 재시작")
        must_click(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 클릭")
        time.sleep(2.0)

    # 어휘 나무 탐색
    if poco("com.kyowon.literacy:id/tree").exists():
        step("어휘 탐험(어휘 나무) 감지됨 🔍")
        fruits = poco("com.kyowon.literacy:id/voca_container").children()
        for fruit in fruits:
            must_click(fruit, f"과일 선택({get_label(fruit)})")
            time.sleep(0.2)
            step(f"단어: {get_label(poco('com.kyowon.literacy:id/text_voca'))}")
            must_click(poco("com.kyowon.literacy:id/btn_close"), "닫기 버튼 클릭")
        time.sleep(0.5)
        try_check(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 감지")

    # 어휘 탐험(일반 영상)
    elif poco("com.kyowon.literacy:id/player_view").exists():
        step("어휘 탐험(일반 영상) 감지됨 🔍")
        time.sleep(0.5)
        if poco("com.kyowon.literacy:id/img_center_replay").exists():
            try_check(poco("com.kyowon.literacy:id/img_center_replay"), "리플레이 버튼 감지 → 재생")
            must_click(poco("com.kyowon.literacy:id/img_center_replay"), "리플레이 버튼 클릭")
            time.sleep(1.0)
            handle_exceptions()
        if poco("com.kyowon.literacy:id/img_bottom_play_pause").exists():
            try_click(poco("com.kyowon.literacy:id/img_bottom_play_pause"), "재생/일시정지 버튼 클릭", fast=True)
            time.sleep(1.0)
    
        time.sleep(1.0)
        MAX_RETRY = 3
        ok = False

        for attempt in range(1, MAX_RETRY + 1):
            step(f"영상 컨트롤러 감지 시도 {attempt}/{MAX_RETRY}")

            # 1) 반드시 눌러야 하는 뷰
            step(f"화면 영역 클릭 ({attempt}회차)")
            obj = poco("com.kyowon.literacy:id/player_view")
            obj_W, obj_H = _get_resolution()
            obj_x1, obj_y1, obj_x2, obj_y2 = _get_region_from_poco(obj, screen_w=obj_W, screen_h=obj_H, debug=False)

            # 우측 끝(너무 끝이면 클릭 미스/화면 밖 방지용으로 2~8px 안쪽 권장)
            obj_x = int((obj_x1 + obj_x2) / 2)
            obj_y = int(obj_y2 - 70)

            # 필요하면 추가 오프셋 적용(예: (510,0) 같은 방식)
            obj_x += 0
            obj_y += 0

            step("영상 하단 부 2회 터치")
            touch((obj_x, obj_y))
            touch((obj_x, obj_y))

            # 2) 성공 여부가 중요한 체크
            ok = try_check(
                poco("com.kyowon.literacy:id/custom_seekbar"),
                f"영상 컨트롤러 감지 ({attempt}회차)"
            )

            if ok:
                step(f"⚠️ 영상 컨트롤러 감지 성공 → 영상 시청 완료 시도")
                poco_obj = poco("com.kyowon.literacy:id/custom_seekbar")
                W, H = _get_resolution()
                x1, y1, x2, y2 = _get_region_from_poco(poco_obj, screen_w=W, screen_h=H, debug=False)

                # 우측 끝(너무 끝이면 클릭 미스/화면 밖 방지용으로 2~8px 안쪽 권장)
                x = int(x2) - 6
                y = int((y1 + y2) / 2)

                # 필요하면 추가 오프셋 적용(예: (510,0) 같은 방식)
                x += 0
                y += 0
                touch((x, y))

                must_check(poco("com.kyowon.literacy:id/img_center_replay"), "리플레이 버튼 확인", timeout=10)

                break

            step(f"⚠️ 영상 컨트롤러 감지 실패 → 재시도")

        # 3) 최종 실패 처리 (Airtest 리포트 Failed)
        if not ok:
            soft_fail("영상 컨트롤러 감지: FAIL ❌(3회 시도 모두 실패)")
            raise AssertionError(
                "영상 컨트롤러 감지 실패 (3회 시도 모두 실패)"
            )

    # 어휘 탐험(어휘 카드/한 컷 툰)
    elif poco("com.kyowon.literacy:id/view_pager").exists():
        step("어휘 탐험(어휘 카드/한 컷 툰) 감지됨 🔍")
        while(True):
            if poco("com.kyowon.literacy:id/btnRetry").exists():
                step("다시 하기 버튼 확인")
                break
            must_click(poco("com.kyowon.literacy:id/btn_next"), "다음 버튼 클릭")

    else:
        handled = handle_exceptions()
        if handled > 0:
            step(f"예외 처리 완료: {handled}건")
            return
        step("어휘 탐험: WARN ⚠️(해당 유형 없음 → SKIP 처리)")
        raise Exception("어휘 탐험: 해당 유형 없음 → 스킵")

# ----- step_block: 어휘 놀이 공통 함수(일반 호출로도 사용 가능)
def first_voca_play_func():
    handle_exceptions()
    while(True):
        time.sleep(1.0)
        progress = get_label(poco("com.kyowon.literacy:id/progress_step_text"))
        m = re.search(r"\d+\s*/\s*(\d+)", progress)
        max_n = int(m.group(1)) if m else None
        if poco("com.kyowon.literacy:id/progress_step_text", text=f"{max_n} / {max_n}").exists():
            step(f"진행률 {max_n} / {max_n} 도달")
            break

        if poco("com.kyowon.literacy:id/btnRetry").exists():
            step("다시 하기 버튼 감지 → 활동 재시작")
            must_click(poco("com.kyowon.literacy:id/btnRetry"), "다시 하기 버튼 클릭")
            time.sleep(1.0)

        if poco("com.kyowon.literacy:id/drop_zone").exists():
            step("어휘 놀이 드래그형 감지 🔍")
            answers = poco("com.kyowon.literacy:id/choice_container").children().child("android.widget.TextView")
            target = poco("com.kyowon.literacy:id/drop_zone")
            for answer in answers:
                must_drag(answer, target, f"보기 선택({get_label(answer)})")
                time.sleep(1.0)
                if progress != get_label(poco("com.kyowon.literacy:id/progress_step_text")):
                    step(f"{get_label(answer)}: 정답 ✅ ({progress}) → ({get_label(poco('com.kyowon.literacy:id/progress_step_text'))})")
                    break
                else:
                    step(f"{get_label(answer)}: 오답 ⚠️ ({progress})")
            else:
                soft_fail("어휘 놀이 기능(드래그형): FAIL ❌ - 다음으로 진행 불가")
                raise RuntimeError("[ERR] 어휘 놀이 기능(드래그형) 실패 - 다음으로 진행 불가")
        else:
            step("어휘 놀이 보기 선택형 감지 🔍")
            answers = poco("com.kyowon.literacy:id/choice_container").children().child("android.widget.TextView")
            for answer in answers:
                must_click(answer, f"보기 클릭({get_label(answer)})")
                time.sleep(3.0)
                if progress != get_label(poco("com.kyowon.literacy:id/progress_step_text")):
                    step(f"{get_label(answer)}: 정답 ✅ ({progress}) → ({get_label(poco('com.kyowon.literacy:id/progress_step_text'))})")
                    break
                else:
                    step(f"{get_label(answer)}: 오답 ⚠️ ({progress})")

            else:
                soft_fail("어휘 놀이 기능(보기 선택형): FAIL ❌ - 다음으로 진행 불가")
                raise RuntimeError("[ERR] 어휘 놀이 기능(보기 선택형) 실패 - 다음으로 진행 불가")


# ========== 메인 플로우 ==========
# Test 플로우
def flow_test():
    step("테스트 플로우1 시작")
    step_block(first_training_func, "술술 읽기 훈련 기능")
    # step_block(first_reading_act_func, "독서 활동 기능")
    # step_block(first_voca_adv_func, "어휘 탐험 기능")
    # step_block(first_voca_play_func, "어휘 놀이 기능")


# ========= 실행 함수 ============
def run_test(serial=None):
    flows = [
        ("테스트 플로우", flow_test),
    ]
    run_literacy_tc(
        flows, serial=serial,
        suite="main_first",
        runner="literacy_test",
        repeat=1,
        need_restart_app=False, 
        need_resource_monitor=False,
        need_app_ready=False,
        need_on_close=False,
        stop_on_fail=False,
        )

if __name__ == "__main__":
    run_test(os.environ.get("ANDROID_SERIAL") or os.environ.get("ADB_SERIAL"))

