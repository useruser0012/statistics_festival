import os
print("현재 작업 디렉토리:", os.getcwd())
print("디렉토리 내 파일 목록:", os.listdir())

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    print("인증 성공!")
except Exception as e:
    print("인증 실패:", str(e))
    st.error(f"Google Sheets 인증에 실패했습니다: {e}")
