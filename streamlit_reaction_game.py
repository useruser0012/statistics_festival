import os
st.write("현재 작업 디렉토리:", os.getcwd())
st.write("디렉토리 내 파일 목록:", os.listdir())
st.write("json 파일 존재 여부:", os.path.isfile('statistics-festival-178f7f9532ad.json'))

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    st.write("Google Sheets 인증 성공!")
except Exception as e:
    st.error(f"Google Sheets 인증에 실패했습니다. service_account.json 파일을 확인해주세요.\n\n오류 메시지: {str(e)}")
