"""
테스트 계정 설정
GitHub Actions 환경에서는 Secrets → 환경변수로 주입됩니다.
로컬 실행 시에는 환경변수를 직접 설정하거나 아래 fallback 값을 채워주세요.
"""

import os

TEST_ID = os.environ.get("TEST_ID", "")
TEST_PW = os.environ.get("TEST_PW", "")

if not TEST_ID or not TEST_PW:
    raise EnvironmentError(
        "환경변수 TEST_ID, TEST_PW가 설정되지 않았습니다.\n"
        "GitHub Secrets 또는 로컬 환경변수를 확인하세요."
    )
