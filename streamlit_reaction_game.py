import streamlit as st
import time
import random
import datetime

import gspread
from google.oauth2.service_account import Credentials

# 구글 API 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("도파민 타이밍 게임 기록").sheet1

# 반별 시간 조작 비율
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
    max_tries_for_max_loss = 100
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
    st.session_state.result_message = ""
    st.session_state.phase = "start"
    st.session_state.start_time = None
    st.session_state.reaction_time = None
    st.session_state.result = ""

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1
if 'phase' not in st.session_state:
    st.session_state.phase = "start"
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
            st.experimental_rerun()

# 게임 페이지
elif st.session_state.page == 'game':
    st.title("도파민 타이밍 게임")
    user_name = st.session_state.user_name
    class_num = st.session_state.class_num
    time_factor = class_settings[class_num]["time_factor"]
    phase = st.session_state.phase

    st.write(f"👤 {user_name}님 | 🏫 {class_num}반")
    st.write(f"🔁 시도: {st.session_state.tries} | ✅ 성공: {st.session_state.successes} | ❌ 실패: {st.session_state.failures} | 🪙 코인: {st.session_state.coins}")

    message = ""
    if phase == "start":
        message = "버튼이 초록색으로 바뀌면 최대한 빨리 클릭하세요!"
    elif phase == "wait":
        message = "준비하세요... 곧 시작됩니다!"
    elif phase == "react":
        message = "🟢 지금 클릭하세요!"
    elif phase == "result":
        message = f"⏱ 반응 속도: {st.session_state.reaction_time}초"

    st.markdown(
        f"""
        <div style="height: 80px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

    if phase == "start":
        if st.button("게임 시작"):
            # 대기 시간 설정 후 phase 전환
            st.session_state.wait_start_time = time.time() + random.uniform(1.5, 3.0)
            st.session_state.phase = "wait"
            st.experimental_rerun()

    elif phase == "wait":
        # 타이머 대기
        if time.time() < st.session_state.wait_start_time:
            st.write("잠시만 기다려 주세요...")
            st.stop()  # 이 시점에서 화면 멈춤, 이후 새로고침 시 상태 다시 체크
        else:
            st.session_state.start_time = time.time()
            st.session_state.phase = "react"
            st.experimental_rerun()

    elif phase == "react":
        if st.button("클릭!"):
            raw_time = time.time() - st.session_state.start_time
            reaction_time = raw_time * time_factor
            st.session_state.reaction_time = round(reaction_time, 3)
            st.session_state.tries += 1

            if reaction_time > 3.0:
                st.session_state.failures += 1
                loss = calculate_failure_coin_loss(st.session_state.tries)
                st.session_state.coins -= loss
                st.session_state.result = f"❌ 3초 초과로 실패! 코인 {loss}개 손실."
            else:
                st.session_state.successes += 1
                gain = random.randint(30, 100)
                st.session_state.coins += gain
                st.session_state.result = f"✅ 반응시간 {reaction_time:.3f}초, 코인 {gain}개 획득!"

            st.session_state.phase = "result"
            st.experimental_rerun()

    elif phase == "result":
        st.markdown(f"### {st.session_state.result}")
        if st.button("다시 도전"):
            st.session_state.phase = "start"
            st.experimental_rerun()

    if st.session_state.tries >= 1000:
        st.write("📊 최대 시도에 도달했습니다. 설문조사로 이동합니다.")
        st.session_state.page = 'survey'
        st.experimental_rerun()

    if st.button("게임 종료 후 설문조사"):
        st.session_state.page = 'survey'
        st.experimental_rerun()

# 설문조사 페이지
elif st.session_state.page == 'survey':
    st.title("설문조사")
    st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

    q1 = st.radio("게임의 흥미도는 어땠나요?", options=["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("게임이 공정하다고 느꼈나요?", options=["매우 공정함", "공정함", "보통", "공정하지 않음"])
    q3 = st.radio("게임 중 충동을 느꼈나요?", options=["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
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

        # 초기화 후 시작 페이지로
        st.session_state.page = "start"
        st.session_state.user_name = ""
        st.session_state.class_num = 1
        reset_game()
        st.experimental_rerun()
