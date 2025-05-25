import streamlit as st
import time
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

# 구글 시트 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("도파민 타이밍 게임 기록").sheet1

# 반별 시간 조작 설정
class_settings = {
    1: {"time_factor": 1.0},
    2: {"time_factor": 0.8},
    3: {"time_factor": 1.0},
    4: {"time_factor": 1.3},
    5: {"time_factor": 1.0},
    6: {"time_factor": 0.8},
    7: {"time_factor": 1.0},
    8: {"time_factor": 1.0},
    9: {"time_factor": 1.3},
    10: {"time_factor": 0.8},
}

def calculate_failure_coin_loss(tries):
    min_loss = 30
    max_loss = 120
    if tries >= 100:
        return random.randint(90, max_loss)
    loss_min = min_loss + (max_loss - min_loss) * (tries / 100)
    loss_max = 50 + (max_loss - 50) * (tries / 100)
    return random.randint(int(loss_min), int(loss_max))

def reset_game():
    st.session_state.tries = 0
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.coins = 10
    st.session_state.state = 'ready'
    st.session_state.next_click_time = 0
    st.session_state.reaction_start_time = 0
    st.session_state.result_message = ""

# 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1
if 'tries' not in st.session_state:
    reset_game()

# 시작 페이지
if st.session_state.page == 'start':
    st.title("도파민 타이밍 게임")
    st.session_state.user_name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
    st.session_state.class_num = st.selectbox("반을 선택하세요", list(range(1, 11)), index=st.session_state.class_num - 1)
    if st.button("게임 시작"):
        if not st.session_state.user_name.strip():
            st.warning("이름을 입력해 주세요.")
        else:
            reset_game()
            st.session_state.page = 'game'

# 게임 페이지
elif st.session_state.page == 'game':
    st.title("도파민 타이밍 게임 진행 중")
    user_name = st.session_state.user_name
    class_num = st.session_state.class_num
    time_factor = class_settings[class_num]["time_factor"]

    st.write(f"{user_name}님, {class_num}반 게임 중입니다.")
    st.write(f"총 시도: {st.session_state.tries} | 성공: {st.session_state.successes} | 실패: {st.session_state.failures} | 코인: {st.session_state.coins}")
    
    if st.session_state.result_message:
        st.markdown(st.session_state.result_message)

    now = time.time()

    if st.session_state.state == 'ready':
        if st.button("시작"):
            delay = random.uniform(0.05, 0.5)
            st.session_state.next_click_time = now + delay
            st.session_state.state = 'waiting'
            st.session_state.result_message = ""
            st.session_state.tries += 1

    elif st.session_state.state == 'waiting':
        st.write("준비 중... 잠시만 기다려주세요.")
        if time.time() >= st.session_state.next_click_time:
            st.session_state.state = 'click_now'
            st.session_state.reaction_start_time = time.time()
        else:
            time.sleep(0.1)  # 0.1초 대기
            st.rerun()

    elif st.session_state.state == 'click_now':
        if st.button("클릭!"):
            raw_reaction_time = time.time() - st.session_state.reaction_start_time
            reaction_time = raw_reaction_time * time_factor

            st.write(f"반응시간: {reaction_time:.3f}초")

            if reaction_time < 0.2:
                st.warning("너무 빨리 클릭하셨습니다! 실패 처리됩니다.")
                st.session_state.failures += 1
                loss = calculate_failure_coin_loss(st.session_state.tries)
                st.session_state.coins -= loss
                st.session_state.result_message = f"너무 빠른 클릭으로 실패! 코인 {loss}개 손실."
            elif reaction_time > 1.5:
                st.warning("너무 늦게 클릭하셨습니다! 실패 처리됩니다.")
                st.session_state.failures += 1
                loss = calculate_failure_coin_loss(st.session_state.tries)
                st.session_state.coins -= loss
                st.session_state.result_message = f"너무 늦은 클릭으로 실패! 코인 {loss}개 손실."
            else:
                st.success("성공했습니다!")
                st.session_state.successes += 1
                gain = random.randint(30, 100)
                st.session_state.coins += gain
                st.session_state.result_message = f"반응시간 {reaction_time:.3f}초, 코인 {gain}개 획득!"

            st.session_state.state = 'ready'

    if st.session_state.tries >= 1000:
        st.write("최대 시도 횟수에 도달했습니다. 설문조사 페이지로 이동합니다.")
        st.session_state.page = 'survey'

    if st.button("게임 종료 후 설문조사"):
        st.session_state.page = 'survey'


# 설문조사 페이지
elif st.session_state.page == 'survey':
    st.title("설문조사")
    st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

    q1 = st.radio("게임의 흥미도는 어땠나요?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("게임이 공정하다고 느꼈나요?", ["매우 공정함", "공정함", "보통", "공정하지 않음"])
    q3 = st.radio("게임 중 충동을 느꼈나요?", ["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
    q4 = st.text_area("비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

    if st.button("설문 제출"):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [now_str, st.session_state.user_name, st.session_state.class_num,
                st.session_state.tries, st.session_state.successes,
                st.session_state.failures, st.session_state.coins,
                q1, q2, q3, q4]

        try:
            sheet.append_row(data)
            st.success("설문이 제출되었습니다! 감사합니다.")
        except Exception as e:
            st.error(f"설문 제출 중 오류 발생: {e}")

        # 상태 초기화
        st.session_state.page = "start"
        st.session_state.user_name = ""
        st.session_state.class_num = 1
        reset_game()
