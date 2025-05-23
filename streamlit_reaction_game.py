import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "/mount/src/statistics_festival/service_account.json"
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=[
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
])

gc = gspread.authorize(credentials)  # 여기서 인증 시도됨
