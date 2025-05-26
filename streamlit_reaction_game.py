import streamlit as st
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

# 구글 스프레드시트 연결 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("도파민 타이밍 게임 기록").sheet1

def reset_game():
    st.session_state.coins = 10
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.tries = 0

def get_success_probability(class_num):
    if class_num in [1,3,5,7,9]:
        return 0.4
    elif class_num in [2,6,10]:
        return 0.2
    elif class_num in [4,8]:
        return 0.9
    else:
        return 0.5

def play_round(class_num):
    prob = get_success_probability(class_num)
    success_flag = random.random() < prob
    coin_change = random.randint(30, 120)
    if success_flag:
        st.session_state.coins += coin_change
        st.session_state.successes += 1
        message = f"성공! 코인이 +{coin_change} 만큼 증가했습니다."
    else:
        st.session_state.coins -= coin_change
        st.session_state.failures += 1
        message = f"실패... 코인이 -{coin_change} 만큼 감소했습니다."
    st.session_state.tries += 1
    return message

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'coins' not in st.session_state:
    reset_game()
if 'user_name' not in st.session_state:
    st.session_state.user_name = ''
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1
if 'successes' not in st.session_state:
    st.session_state.successes = 0
if 'failures' not in st.session_state:
    st.session_state.failures = 0
if 'tries' not in st.session_state:
    st.session_state.tries = 0

if st.session_state.page == 'start':
    st.title("게임 시작 페이지")
    user_name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
    class_num = st.number_input("반을 입력하세요 (1~10)", min_value=1, max_value=10, step=1, value=st.session_state.class_num)
    if st.button("게임 시작") and user_name.strip() != "":
        st.session_state.user_name = user_name
        st.session_state.class_num = class_num
        reset_game()
        st.session_state.page = 'game'
        st.experimental_rerun()

elif st.session_state.page == 'game':
    st.title("카드 맞추기 게임")
    st.write(f"플레이어: {st.session_state.user_name} / 반: {st.session_state.class_num}")
    st.write(f"현재 코인: {st.session_state.coins}")
    st.write(f"도전 횟수: {st.session_state.tries}, 성공: {st.session_state.successes}, 실패: {st.session_state.failures}")

    if st.button("카드 선택 (1/2 확률 게임)"):
        result_message = play_round(st.session_state.class_num)
        st.write(result_message)
        st.write(f"현재 코인: {st.session_state.coins}")

    if st.button("그만하기 (게임 종료 및 설문조사)"):
        st.session_state.page = 'survey'
        st.experimental_rerun()

elif st.session_state.page == 'survey':
    st.title("설문조사")
    st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

    q1 = st.radio("게임의 흥미도는 어땠나요?", options=["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("게임이 공정하다고 느꼈나요?", options=["매우 공정함", "공정함", "보통", "공정하지 않음"])
    q3 = st.radio("게임 중 충동을 느꼈나요?", options=["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
    q4 = st.text_area("비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

    if st.button("설문 제출"):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [
            now_str,
            st.session_state.user_name,
            st.session_state.class_num,
            st.session_state.tries,
            st.session_state.successes,
            st.session_state.failures,
            st.session_state.coins,
            q1,
            q2,
            q3,
            q4
        ]
        try:
            sheet.append_row(data)
            st.success("설문이 제출되었습니다! 감사합니다.")
            reset_game()
            st.session_state.user_name = ''
            st.session_state.class_num = 1
            st.session_state.page = 'start'
            st.experimental_rerun()
        except Exception as e:
            st.error(f"설문 제출 중 오류 발생: {e}")
