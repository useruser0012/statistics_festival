from google.oauth2.service_account import Credentials
import gspread

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file('statistics-festival-6037ec1a564b.json', scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("도파민 타이밍 게임 기록").sheet1
