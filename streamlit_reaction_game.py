import streamlit as st
import random
import time
import datetime
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- 구글 스프레드시트 설정 ---
SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'statistics-festival-178f7f9532ad.json'  # 서비스 계정 JSON 파일 경로
SPREADSHEET_ID = '14AcGHQwN8ydeUEPvxGWEl4mB7sueY1g9TV9fptMJpiI'

# 서비스 계정 파일 존재 확인
if not os.path.isfile(SERVICE_ACCOUNT_FILE):
    st.error(f"서비스 계정 인증 파일이 없습니다: {SERVICE_ACCOUNT_FILE}")
    st.stop()

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
except Exception as e:
    st.error(f"구글 인증 또는 서비스 빌드 실패: {e}")
    st.stop()

# --- 클래스별 성공률 및 시간 조작 비율 설정 (1~10반) ---
class_settings = {
    1: {"success_rate": 0.6, "time_factor": 1.0},
    2: {"success_rate": 0.99, "time_factor": 0.8},
    3: {"success_rate": 0.6, "time_factor": 1.0},
    4: {"success_rate": 0.05, "time_factor": 1.3},
    5: {"success_rate": 0.6, "time_factor": 1.0},
    6: {"success_rate": 0.99, "time_factor": 0.8},
    7: {"success_rate": 0.6, "time_factor": 1.0},
    8: {"success_rate": 0.6, "time_factor": 1.0},
    9: {"success_rate": 0.05, "time_factor": 1.3},
    10: {"success_rate": 0.99, "time_factor": 0.8},
}

# --- Streamlit 상태변수 초기화 ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1
if 'tries' not in st.session_state:
    st.session_state.tries = 0
if 'successes' not in st.session_state:
    st.session_state.successes = 0
if 'failures' not in st.session_state:
    st.session_state.failures = 0
if 'coins' not in st.session_state:
    st.session_state.coins = 10  # 초기 코인 10개
if 'game_in_progress' not in st.session_state:
    st.session_state.game_in_progress = False
if 'waiting_for_click' not in st.session_state:
    st.session_state.waiting_for_click = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0

# --- UI ---
st.title("도파민 타이밍 게임")

user_name = st.text_input("이름을 입력하세요", key='user_name')
class_num = st.selectbox("반을 선택하세요", list(range(1, 11)), key='class_num')

success_rate = class_settings[class_num]["success_rate"]
time_factor = class_settings[class_num]["time_factor"]

# --- 코인 손실 계산 함수 ---
def calculate_failure_coin_loss(tries):
    """
    시도 횟수에 따라 실패 시 잃는 코인 수 증가.
    30~50에서 시작해 최대 120까지 선형 증가.
    """
    min_loss = 30
    max_loss = 120
    max_tries_for_max_loss = 100  # 100번 시도 시 최대 손실

    if tries >= max_tries_for_max_loss:
        return random.randint(90, max_loss)
    else:
        loss_min = min_loss + (max_loss - min_loss) * (tries / max_tries_for_max_loss)
        loss_max = 50 + (max_loss - 50) * (tries / max_tries_for_max_loss)
        return random.randint(int(loss_min), int(loss_max))

def reset_game():
    st.session_state.tries = 0
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.coins = 10
    st.session_state.game_in_progress = False
    st.session_state.waiting_for_click = False
    st.session_state.start_time = 0

def start_trial():
    st.session_state.tries += 1
    st.session_state.waiting_for_click = True
    st.session_state.start_time = time.time()

def stop_game():
    st.session_state.game_in_progress = False
    st.session_state.waiting_for_click = False
    st.write("게임이 중단되었습니다.")

def game_loop():
    st.markdown(f"**총 도전 횟수:** {st.session_state.tries}  |  **성공 횟수:** {st.session_state.successes}  |  **실패 횟수:** {st.session_state.failures}  |  **현재 코인:** {st.session_state.coins}")

    if st.session_state.waiting_for_click:
        if st.button("지금 클릭!"):
            reaction_time = time.time() - st.session_state.start_time
            if reaction_time < 0.1:
                st.warning("너무 빨리 클릭하셨습니다! 실패로 처리됩니다.")
                st.session_state.failures += 1
                coin_loss = calculate_failure_coin_loss(st.session_state.tries)
                st.session_state.coins -= coin_loss
                st.write(f"코인 {coin_loss}개를 잃었습니다.")
                st.session_state.waiting_for_click = False
            else:
                if random.random() <= success_rate:
                    st.success(f"성공! 반응 시간: {reaction_time:.2f}초")
                    st.session_state.successes += 1
                    coin_gain = random.randint(30, 100)
                    st.session_state.coins += coin_gain
                    st.write(f"코인 {coin_gain}개를 획득했습니다!")
                else:
                    st.error(f"실패... 반응 시간: {reaction_time:.2f}초")
                    st.session_state.failures += 1
                    coin_loss = calculate_failure_coin_loss(st.session_state.tries)
                    st.session_state.coins -= coin_loss
                    st.write(f"코인 {coin_loss}개를 잃었습니다.")
                st.session_state.waiting_for_click = False

            if st.session_state.coins < 0:
                st.session_state.coins = 0

    else:
        if st.session_state.tries < 1000:
            if st.button("다음 시도 시작"):
                start_trial()
        else:
            st.write("최대 시도 횟수에 도달했습니다.")
            st.session_state.game_in_progress = False

# --- 메인 게임 흐름 ---
if not st.session_state.game_in_progress:
    if st.button("게임 시작"):
        if not user_name:
            st.warning("이름을 입력해 주세요.")
        else:
            reset_game()
            st.session_state.game_in_progress = True
            start_trial()

if st.session_state.game_in_progress:
    st.write(f"{user_name}님, {class_num}반 게임 진행 중입니다.")
    game_loop()

    if st.button("게임 종료"):
        stop_game()

# 게임 결과 출력
if not st.session_state.game_in_progress and st.session_state.tries > 0:
    st.subheader("게임 결과")
    st.write(f"총 시도: {st.session_state.tries}")
    st.write(f"성공: {st.session_state.successes}")
    st.write(f"실패: {st.session_state.failures}")
    st.write(f"코인: {st.session_state.coins}")

# --- 설문조사 ---
st.subheader("설문조사")

q1 = st.radio("게임의 흥미도는 어땠나요?", options=["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
q2 = st.radio("게임이 공정하다고 느꼈나요?", options=["매우 공정함", "공정함", "보통", "공정하지 않음"])
q3 = st.radio("게임 중 충동을 느꼈나요?", options=["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
q4 = st.text_area("비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

if st.button("설문 제출"):
    if not st.session_state.user_name:
        st.warning("이름을 입력해 주세요.")
    else:
        try:
            values = [
                st.session_state.user_name,
                st.session_state.class_num,
                st.session_state.tries,
                st.session_state.successes,
                st.session_state.failures,
                st.session_state.coins,
                str(datetime.datetime.now()),
                q1,
                q2,
                q3,
                q4
            ]
            request = sheet.values().append(
                spreadsheetId=SPREAD
if st.button("설문 제출"):
    if not st.session_state.user_name:
        st.warning("이름을 입력해 주세요.")
    else:
        try:
            values = [
                st.session_state.user_name,
                st.session_state.class_num,
                st.session_state.tries,
                st.session_state.successes,
                st.session_state.failures,
                st.session_state.coins,
                str(datetime.datetime.now()),
                q1,
                q2,
                q3,
                q4
            ]
            request = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range="Sheet1!A1",  # 시트 이름과 범위 조정 필요
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [values]}
            )
            response = request.execute()
            st.success("설문이 성공적으로 제출되었습니다. 참여해 주셔서 감사합니다!")
        except Exception as e:
            st.error(f"설문 제출 중 오류가 발생했습니다: {e}")
