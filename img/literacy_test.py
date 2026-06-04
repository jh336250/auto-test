# =================================================
# QA 자동화 스크립트 - 문해력 TC 공통 러너
# 👤 Author: Eden Kim
# 📅 Date: 2026-01-23 - v1.0.5
#   - cleanup_rolling_logs 함수 추가(산출물 용량 절감)
#   - 예외처리 추가: 자동 완성 저장 팝업, AI 술술 읽기 평가, 주차 이동 불가 팝업
#   - need_app_ready 인자 추가: 빠른 Test를 위해 app_ready 과정 닫기옵션
#   - 예외처리 명칭 수정, AI 술술 읽기 평가, 주차 이동 불가 팝업, 리포트 화면 닫기 추가
#   - 목표 단계(TARGET_LEVEL) 전역 변수화 및 메인 입장 시 현재 단계 자동 감지
#   - PACKAGE_ALIASES 지원 추가, 리소스 ID 셀렉터 자동 치환 헬퍼 설치
# =================================================
#   - Airtest + Poco 기반 안드로이드 앱 자동화 스크립트
#   - 공통 함수 및 플로우 관리
#   - 테스트 케이스 작성 및 관리
#   - 리포트 및 결과 분석
# =================================================
# -*- encoding=utf8 -*-
import os, sys, webbrowser, time
from airtest.core.api import *
from airtest.report.report import simple_report
from datetime import datetime
from poco.drivers.unity3d import UnityPoco
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from pathlib import Path

# 공통 모듈 로딩 및 환경 변수 설정
SCRIPT_DIR = os.getenv("QA_SCRIPT") or Path(__file__).resolve().parent.parent
OUT_ROOT   = os.path.join(SCRIPT_DIR, "result")
os.makedirs(OUT_ROOT, exist_ok=True)   # 폴더 없으면 생성, 이미 있으면 무시
TOOLKIT = os.getenv("QA_TOOLKIT") or os.path.join(SCRIPT_DIR, "qa_common")
if TOOLKIT and TOOLKIT not in sys.path: sys.path.insert(0, TOOLKIT)
from common import *

# 프로젝트별 설정
PACKAGE    = "com.kyowon.literacy"

# ✅ 이전/별칭 패키지들(기존 하드코딩 selector 대응용)
PACKAGE_ALIASES = [
    "com.kyowon.literacy",
    "com.kyowon.literacy.store",
]
MAX_REPEAT = 2  # 플로우 전체 반복 횟수
MAX_COUNT = 3   # 플로우내 스크롤탐색 최대 반복 횟수
RESTART_DELAY = 3.0
UI_MODE = "native" # unity / native
# 메일 받는이 변경 시 사용 (None = 환경변수 적용)
MAIL_TO    = None
MAIL_CC    = "edenkim0316@gmail.com"
MAIL_BCC   = None

WORKER_ID = None
POOL_NAME = f"{PACKAGE}_accounts"  # 결과: _accounts/패키지명_accounts.json

TARGET_LEVEL = None

# ✅ 앱별 계정풀 파일명 지정
#   - pool_file 로 전체 경로 지정도 가능(절대/상대)
#   - 미지정 시 기본값 사용
configure_account_pool(pool_name=POOL_NAME)

# ============== 앱별 공통 함수 ===============
# 앱 개별 시작
def literacy_start():
    time.sleep(2)

    # 홈으로 나갔다가 내부 런처 통해 진입
    keyevent("HOME")
    time.sleep(2)
    
    # 내부 런처가 끼어들어서 그냥 start로는 안 뜨는 케이스
    try:
        must_click(poco("kr.co.kyowon.launcher:id/tap_membership"), "[런처] 멤버십 탭")
        scroll_until_visible(
                target_element=poco(text="초등 읽기 프로젝트 퍼펙트 문해"),
                direction="right", step_ratio=0.5, duration=0.5,
                scroll_view=poco("kr.co.kyowon.launcher:id/recycler_view"),
                debug=False,
            )
        must_click(poco(text="초등 읽기 프로젝트 퍼펙트 문해"), "[런처] 퍼펙트 문해 앱 아이콘 클릭")
        
        # 로고 등장 시 로고 체크
        if poco("com.kyowon.literacy:id/imgv_intro_ci").exists():
            try_check(poco("com.kyowon.literacy:id/imgv_intro_ci"), "📋 [Basic Test / 노출] CI")
            try_check(poco("com.kyowon.literacy:id/imgv_intro_bi"), "📋 [Basic Test / 노출] BI")
            
        return
    except Exception as e:
        soft_fail(f"[ERR] 앱 실행: FAIL - {e}")
        raise   # 이후 흐름 중단

# 권한 체크
def permission_check():
    try:
        # 가능하면 로고 체크
        if poco("com.kyowon.literacy:id/imgv_intro_ci").exists():
            try_check(poco("com.kyowon.literacy:id/imgv_intro_ci"), "📋 [Basic Test / 노출] CI")
            try_check(poco("com.kyowon.literacy:id/imgv_intro_bi"), "📋 [Basic Test / 노출] BI")

        # 업데이트 팝업 닫기
        if poco(text="업데이트 안내").exists():
            must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "업데이트 안내 팝업 닫기")
            time.sleep(2)
            poco(text="ALL&G 단말기 매니저").wait_for_disappearance(timeout=180)
            try_check(poco("com.kyowon.literacy:id/imgv_intro_ci"), "📋 [Basic Test / 노출] CI")
        
        # 권한 허용 팝업 기본 체크
        if poco(text="앱 접근 권한 허용 안내").exists():
            try_check(poco(text="앱 접근 권한 허용 안내"), "📋 [Basic Test / 노출] 권한 허용 안내 팝업")
            must_click(poco("com.kyowon.literacy:id/btn_confirm"))
            
        if poco("com.android.permissioncontroller:id/permission_icon").exists():
            try_check(
                poco("com.android.permissioncontroller:id/permission_icon"),
                "📋 [Basic Test / 노출] 권한 허용 팝업 - 카메라, 파일, 마이크 (파일 미노출 가능)"
            )
            click_until_disappear(
                target_poco=poco("com.android.permissioncontroller:id/permission_allow_foreground_only_button"),
                fallback_poco=None,
                desc="권한 허용 팝업 - 앱 사용 중에만 허용",
                interval=0.5
            )
            
        # 추가 권한 필요 시 진행
        if poco("com.android.permissioncontroller:id/permission_icon").exists():
            try_check(
                poco("com.android.permissioncontroller:id/permission_icon"),
                "추가 팝업 발견"
            )
            click_until_disappear(
                target_poco=poco("com.android.permissioncontroller:id/permission_allow_button"),
                fallback_poco=None,
                desc="권한 허용 팝업 - 허용",
                interval=0.5
            )
            
        return
    except Exception as e:
        soft_fail(f"[ERR] 권한 체크: FAIL - {e}")
        raise   # 이후 흐름 중단
        

# 앱 준비 대기 콜백(앱별 수정 필요, 함수명 고정)
def app_ready(timeout=15, interval=0.5):
    """
    주어진 timeout 동안:
      - 로그인 화면 보이면 → login 실행
      - 메인 화면 보이면 → 플로우 진행
    """
    global TARGET_LEVEL
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            # 앱 포그라운드 상태 확인
            if not is_app_in_foreground():
                step("앱 포그라운드 상태 확인 실패 → 런처 통해 앱 진입")
                restart_app()
                permission_check()

            # 권한 허용 체크가 부족했을 경우 시도
            if poco(text="앱 접근 권한 허용 안내").exists():
                permission_check()

            # 계약 정보 미확인 팝업
            if poco("com.kyowon.literacy:id/text_alert_message").exists():
                must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "계약 정보 팝업 확인")

            # 로그인 화면 요소 체크
            if poco("com.kyowon.literacy:id/btn_login").exists():
                try_check(poco("com.kyowon.literacy:id/btn_login"), "📋 [Basic Test / 노출] 로그인")
                login()

            # 로그인 후 예외처리
            handle_exceptions()

            # 튜토리얼 체크
            if poco("com.kyowon.literacy:id/img_tuto").exists():
                try_check(poco("com.kyowon.literacy:id/img_tuto"), "📋 [Basic Test / 노출] 튜토리얼", timeout=5)
                click_until_disappear(
                    target_poco=poco("com.kyowon.literacy:id/btn_next"),
                    fallback_poco=poco("com.kyowon.literacy:id/btn_start"),
                    desc="📋 [Basic Test / 기능] 튜토리얼",
                    interval=0.5
                )
                time.sleep(2)
    
            # 실전 평가
            if (poco("com.kyowon.literacy:id/img_char") and poco("com.kyowon.literacy:id/btn_alert_negative")).exists():
                try_check(
                    poco("com.kyowon.literacy:id/img_char"), 
                    "📋 [Basic Test / 노출] 문해력 실전 평가", timeout=5
                )
                must_click(poco("com.kyowon.literacy:id/btn_alert_negative"), "📋 [Basic Test / 기능] 문해력 실전 평가")
                
            # 첫 로그인 보상
            if poco(text="문해력 탐험 시작을 환영해요!").exists():
                try_check(
                    poco(text="문해력 탐험 시작을 환영해요!"),
                    "첫 로그인 보상 발견", timeout=5
                )
                must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "첫 로그인 보상 확인")

            # 주차 이동 불가 팝업
            if poco("com.kyowon.literacy:id/text_alert_message", text="이동할 수 없는 주차예요.").exists():
                must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "주차 이동 불가 팝업 확인")

            # 메인화면 요소 체크
            if poco("com.kyowon.literacy:id/top_right_menu").exists():
                step("메인 화면 발견 → flow 진행")
                if exists(Template(r"level1.png", threshold=0.88, rgb=True)):
                    step("1단계 감지 → TARGET_LEVEL 설정")
                    TARGET_LEVEL = "1단계"
                elif exists(Template(r"level2.png", threshold=0.88, rgb=True)):
                    step("2단계 감지 → TARGET_LEVEL 설정")
                    TARGET_LEVEL = "2단계"
                elif exists(Template(r"level3.png", threshold=0.88, rgb=True)):
                    step("3단계 감지 → TARGET_LEVEL 설정")
                    TARGET_LEVEL = "3단계"
                elif exists(Template(r"level4.png", threshold=0.88, rgb=True)):
                    step("4단계 감지 → TARGET_LEVEL 설정")
                    TARGET_LEVEL = "4단계"
                else:
                    step("[WARN] 메인 화면 요소 미검출 → TARGET_LEVEL 기본값(2단계) 설정")
                    TARGET_LEVEL = "2단계"
                return True
            
        except Exception as e:
            msg = str(e)

            # Poco / uiautomation 쪽이 심하게 꼬인 흔적이면 → 하드 리셋 1회 시도
            fatal_keys = [
                "socket connection broken",
                "uiautomation ready",              # still waiting for uiautomation ready
                "Process crashed",                 # INSTRUMENTATION_RESULT: shortMsg=Process crashed.
                "Remote end closed connection",    # RemoteDisconnected
                "EOFError",
            ]

            if any(k in msg for k in fatal_keys):
                step(f"[WARN] app_ready 중 Poco 연결 오류 감지 → 하드 리셋 시도: {msg}")
                try:
                    # env는 common.use_env()에서 가져오는 전역 QAEnv 사용
                    poco_hard_reset(reason="app_ready loop exception")
                    # 리셋 성공했으면, timeout 남은 동안 다시 while 루프 계속
                    continue
                except PocoFatalError as pe:
                    step(f"[FATAL] app_ready 내 poco_hard_reset 실패: {pe!r}", True)
                    # 더 이상 복구 불가 → 그대로 예외 올려서 상위에서 처리
                    raise

            # 그 외의 자잘한 예외는 기존처럼 무시하고 재시도
            # (로그만 남길지, 완전 무시할지는 선택)
            # step(f"[WARN] app_ready 루프 중 예외 무시: {msg}", False)

        time.sleep(interval)

    # 여기까지 오면 timeout
    # 1회만 재시도하도록 플래그 사용
    if not getattr(app_ready, "_retried_once", False):
        app_ready._retried_once = True
        step("[WARN] app_ready: 로그인/메인 화면 요소 미등장 → 앱 재시작 후 1회 재시도")
        restart_app(retries=1)
        permission_check()
        # 재시도: 성공하면 True 반환, 실패하면 아래의 raise로 넘어감
        return app_ready(timeout=timeout, interval=interval)
    else:
        desc = "[ERR] app_ready: FAIL - 로그인/메인 화면 요소 모두 미등장 (재시도 실패)"
        soft_fail(desc)
        try:
            if not slice_path:
                slice_path = save_log(timeout=45)
            if not pdf_path:
                pdf_path   = gen_report(timeout=60)
        except Exception as ee:
            step(f"[WARN] 산출물 확보 중 오류: {ee}")
            note(f"[RISK] 실패 증거 산출물 확보 중 오류(일부 첨부 누락 가능): {desc} ({ee})")

    raise RuntimeError("app_ready 실패")

# 로그인
def login(env: Optional['QAEnv'] = None):
    env = use_env(env)
    try:
        step("로그인 시도")
        # 🔹 수정: 계정 지연 임대 (env._acct 없으면 즉시 할당)
        if not hasattr(env, "_acct"):
            global WORKER_ID
            WORKER_ID, uid, pw = acquire_account()
            env._acct = (uid, pw)
            step(f"[ACCT] acquired (lazy): {uid}")
        else:
            uid, pw = env._acct

        # 🔹 실제 로그인 로직
        must_type(poco("com.kyowon.literacy:id/et_id"), uid)
        must_type(poco("com.kyowon.literacy:id/et_pw"), pw)
        must_click(poco("com.kyowon.literacy:id/btn_login"), "로그인 버튼 클릭")
        
        # 중복 로그인 처리
        if poco(text="중복 로그인").exists():
            must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "중복 로그인 확인")
        
        # 환영 알림 팝업 닫기
        must_click(poco("com.kyowon.literacy:id/btn_alert_positive"), "환영 알림 확인")
        
        # 홈계정 등록 처리
        if poco(text="나중에 하기").exists():
            must_click(poco(text="나중에 하기"), "홈계정 등록 나중에 하기")
        time.sleep(10) # 로그인 처리 대기
    except Exception as e:
        # 실패 시 즉시 스냅샷
        soft_fail(f"[ERR] 로그인: FAIL - {e}", True)
        # save.flag 생성 → logcat_slice 확보
        raise   # 이후 흐름 중단
        
# 로그아웃
def logout():
    try:
        step("로그아웃 시도")
        time.sleep(2)
        must_click(poco("com.kyowon.literacy:id/top_right_menu")
                   .child("android.widget.ImageButton")[2])
        time.sleep(1)
        must_click(poco(text="설정"))
        must_click(poco("com.kyowon.literacy:id/btn_logout"))
        must_click(poco("com.kyowon.literacy:id/btn_alert_positive"))
        poco("com.kyowon.literacy:id/btn_login").wait_for_appearance()
        step("로그아웃 완료", True)
    except Exception as e:
        # 실패 시 즉시 스냅샷
        soft_fail(f"[ERR] 로그아웃: FAIL - {e}")
        raise   # 이후 흐름 중단

# 메인 화면 새로고침 (미사용)
def main_refresh():
    handle_exceptions()
    must_click(poco("TopContaner").offspring(text="열려라!\n지식문"))
    must_click(poco("Btn_Logo").child("touchArea"))

# 예외상황 처리기
def handle_exceptions(debug=False):
    
    # 1) 규칙 구성 (필요한 만큼 자유롭게 추가/수정)
    rules = [
        {
            "name": "자세 확인 닫기(다시 보지 않기)",
            "condition": cond_exists(poco("com.kyowon.literacy:id/txt_check_fluency")),
            "action": multi_act(act_click(poco("com.kyowon.literacy:id/radio")),
                                act_click(poco("android.widget.ImageButton"))),
        },
        {
            "name": "가이드 팝업 닫기(다시 보지 않기)",
            "condition": cond_exists(poco("com.kyowon.literacy:id/txt_today_dont_show")),
            "action": act_click(poco("com.kyowon.literacy:id/btn_skip_today")),
        },
        {
            "name": "학습 가이드 닫기",
            "condition": cond_exists(poco(text="학습 가이드")),
            "action": act_click(poco("com.kyowon.literacy:id/btn_popup_close")),
        },
        {
            "name": "자세 확인 팝업 닫기",
            "condition": cond_exists(poco(text="바른 자세로 앉아 있나요?\n기기를 정면에 세워 두고, 화면을 바라보아요!")),
            "action": act_click(poco("com.kyowon.literacy:id/btn_popup_close")),
        },
        {
            "name": "정답 및 풀이 팝업 닫기",
            "condition": cond_exists(poco(text="정답 및 풀이")),
            "action": act_click(poco("com.kyowon.literacy:id/exitButton")),
        },
        {
            "name": "로딩 대기하기",
            "condition": cond_exists(poco("com.kyowon.literacy:id/layout_progress").child("com.kyowon.literacy:id/img_main_boo_k_tower_progress")),
            "action": (lambda: poco("com.kyowon.literacy:id/layout_progress").child("com.kyowon.literacy:id/img_main_boo_k_tower_progress").wait_for_disappearance(timeout=60.0)),
        },
        {
            "name": "자동 완성 저장 팝업 닫기",
            "condition": cond_exists(poco("android:id/sem_autofill_save_checkbox")),
            "action": multi_act(act_click(poco("android:id/sem_autofill_save_checkbox")),
                                act_click(poco("android:id/autofill_save_yes"))),
        },
        {
            "name": "AI 술술 읽기 평가 감지 🔍 → 진행",
            "condition": cond_exists(poco("com.kyowon.literacy:id/guidePopup").offspring("com.kyowon.literacy:id/btn_close")),
            "action": multi_act(
                act_click(poco("com.kyowon.literacy:id/guidePopup").offspring("com.kyowon.literacy:id/btn_close")),
                act_click(poco("com.kyowon.literacy:id/recordButton")),
                lambda: poco("com.kyowon.literacy:id/completeButton").wait_for_appearance(timeout=120.0),
                act_click(poco("com.kyowon.literacy:id/completeButton")),
                act_click(poco("com.kyowon.literacy:id/finishButton"))
            ),
        },
        {
            "name": "주차 이동 불가 팝업 닫기",
            "condition": cond_exists(poco(text="이동할 수 없는 주차예요.")),
            "action": act_click(poco("com.kyowon.literacy:id/btn_alert_positive")),
        },
        {
            "name": "리포트 닫기",
            "condition": cond_exists(poco(text="오늘도 잘했어요!")),
            "action": act_click(poco(text="X")),
        },
        {
            "name": "홈 계정 등록 팝업 출력 오류 처리",
            "condition": cond_exists(poco(text="나중에 하기")),
            "action": act_click(poco(text="나중에 하기")),
        },
    ]
    
    # 2) 실행 (첫 매칭만 처리: handle_all=False / 여러 개 처리하려면 True)
    handled = handle_expected_exceptions(
        rules=rules,
        handle_all=True,   # 여러 개 한 번에 처리하려면 True
        stop_after=2,        # 무한루프 방지 상한
    )
    if debug: step(f"[EXC] handled={handled}")
    return handled

# =============== 컨텐츠별 플로우 ===============
def flow_myprofile():
    must_click(poco("com.kyowon.literacy:id/profile_img"))
    must_click(poco(text="골랐어요!"))
    step("내 프로필 완료")
    
# ===== TC에서 재사용할 수 있는 경량 러너 =====
def run_literacy_tc(
    flows,
    serial=None,
    *,
    suite: str = "basic",
    runner: str = "literacy_test",
    repeat: int = MAX_REPEAT,
    need_account: bool = True,
    need_restart_app: bool = True,
    need_resource_monitor: bool = True,
    need_app_ready: bool = True,
    need_on_close: bool = True,
    stop_on_fail: bool = False,
    mail_to: str = MAIL_TO,
    mail_cc: str = MAIL_CC,
    mail_bcc: str = MAIL_BCC,
):
    """
    TC 스크립트에서 '플로우 몇 개만' 돌리고 싶을 때 사용하는 공용 진입점.
    finally 안에 있던 모니터 종료, 리포트 생성, 계정 반납을 여기로 모았다.
    """
    global WORKER_ID

    # 1) env 만들기 (main이 하던 그대로)
    env = QAEnv(
        PACKAGE,
        SCRIPT_DIR,
        OUT_ROOT,
        serial=serial,
        per_device_dir=True,
        restart_delay=RESTART_DELAY,
        ui_mode=UI_MODE,
        app_start=literacy_start,
        on_ready=app_ready,
        on_close=logout,
        airtest_script=__file__,

        # ✅ Run Standard v1.0
        suite=suite,
        runner=runner,
        use_run=True,
    )

    # ✅ selector 패키지 자동 치환을 위한 alias 등록
    env.package_aliases = PACKAGE_ALIASES

    # 리소스 ID 셀렉터 자동 치환 헬퍼 설치
    install_poco_selector_autopatch()

    # 🔹 앱 전용 예외 처리기 래퍼 등록
    def _literacy_exc_handler(exc: Exception, e: QAEnv) -> int:
        # 지금은 exc는 안 쓰지만, 나중에 rule에서 필요하면 활용 가능
        try:
            return handle_exceptions()
        except Exception as inner:
            step(f"[EXC] handle_exceptions 실패: {inner}", True, e)
            return 0

    env.handle_exceptions = _literacy_exc_handler

    # 🔹 현재 env 등록 (이후 must_click 등에서 env 안 넘겨도 사용 가능)
    set_current_env(env)

    # 3) 계정 임대 (옵션)
    WORKER_ID = None
    if need_account:
        WORKER_ID, uid, pw = acquire_account()
        env._acct = (uid, pw)
        step(f"[ACCT] acquired: {uid}")

    auto_setup(__file__, logdir=env.airtest_log_dir)

    proc = None

    # 4) 앱 재시작 + 리소스 모니터
    if need_restart_app:
        restart_app()
        permission_check()
    if need_resource_monitor:
        proc = start_resource_monitor()

    # 4-1) on_close 해제 옵션
    if not need_on_close:
        env.on_close = None

    try:
        # 5) 실제 플로우 실행
        if need_app_ready:
            app_ready()

        run_flows(
            flows=flows,
            env=env,
            repeat=repeat,
            send_success_mail_each=False,
            stop_on_fail=stop_on_fail,
            mail_to=mail_to,
            mail_cc=mail_cc,
            mail_bcc=mail_bcc,
        )
        
    finally:
        # A) 모니터 끄고 rolling 로그 삭제
        if proc is not None:
            try:
                stop_resource_monitor()
                # ✅ rolling 로그 삭제(산출물 용량 절감)
                cleanup_rolling_logs(env.out_dir, env=env, keep_latest=False, max_wait=15)
            except Exception:
                pass

        # B) 계정 반납
        if need_account and WORKER_ID:
            try:
                release_account(WORKER_ID)
                step("[ACCT] released")
            except Exception as e:
                step(f"[WARN] account release fail: {e}")

    return env   # 필요하면 TC에서 env 다시 쓸 수 있음

    

# ============== 메인 플로우(자체 실행 시 간단한 확인용) ===============
def main(serial=None):
    
    flows = [
        ("내 프로필 선택", flow_myprofile),
    ]
    run_literacy_tc(
        flows,
        serial=serial,
        need_account=True,
        need_restart_app=True,
    )

if __name__ == "__main__":
    main(os.environ.get("ANDROID_SERIAL") or os.environ.get("ADB_SERIAL"))






