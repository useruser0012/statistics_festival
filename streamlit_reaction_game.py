import streamlit as st
import time
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 구글 시트 연동 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open("도박게임설문").sheet1  # 스프레드시트 제목에 맞게 수정

# --- 페이지 초기화 ---
if 'page' not in st.session_state:
    st.session_state.page = 'start'

# --- 사용자 정보 및 게임 상태 초기화 ---
def reset_game():
    st.session_state.tries = 0
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.coins = 0

# --- 시작 페이지 ---
if st.session_state.page == 'start':
    st.title("🎮 확률형 반응속도 게임")
    st.write("아래 정보를 입력하고 시작하세요.")

    st.session_state.user_name = st.text_input("이름을 입력하세요")
    st.session_state.class_num = st.selectbox("반을 선택하세요", [1, 2, 3, 4])

    if st.button("게임 시작") and st.session_state.user_name:
        reset_game()
        st.session_state.page = 'game'
        st.rerun()

# --- 게임 페이지 ---
elif st.session_state.page == 'game':
    st.title("🚀 반응 속도 게임")

    st.write(f"👤 이름: {st.session_state.user_name} | 🏫 반: {st.session_state.class_num}")
    st.write(f"🔁 시도 횟수: {st.session_state.tries} | ✅ 성공: {st.session_state.successes} | ❌ 실패: {st.session_state.failures}")
    st.write(f"🪙 보유 코인: {st.session_state.coins}")

    if 'waiting' not in st.session_state:
        st.session_state.waiting = False
    if 'reaction_start' not in st.session_state:
        st.session_state.reaction_start = 0

    if not st.session_state.waiting:
        if st.button("🔵 시작 버튼을 누르세요!"):
            st.session_state.waiting = True
            wait_time = random.uniform(2, 5)
            st.session_state.reaction_start = time.time() + wait_time
            time.sleep(wait_time)
            st.rerun()
    else:
        current_time = time.time()
        if current_time < st.session_state.reaction_start:
            st.write("⏳ 잠시만 기다리세요...")
        else:
            st.write("🟢 지금 클릭하세요!")
            if st.button("클릭!"):
                reaction_time = time.time() - st.session_state.reaction_start
                st.session_state.tries += 1

                # 성공률 조작
                class_num = st.session_state.class_num
                success = False
                if class_num == 1:  # 1반: 매우 유리
                    success = reaction_time < 0.6
                elif class_num in [2, 3]:  # 2,3반: 보통
                    success = reaction_time < 0.35
                elif class_num == 4:  # 4반: 매우 불리
                    success = reaction_time < 0.2

                if success:
                    st.session_state.successes += 1
                    st.session_state.coins += 100
                    st.success(f"성공! 반응시간: {reaction_time:.3f}초")
                else:
                    st.session_state.failures += 1
                    st.warning(f"실패! 반응시간: {reaction_time:.3f}초")

                st.session_state.waiting = False

    if st.session_state.tries >= 10:
        st.success("10번의 게임이 끝났습니다!")
        if st.button("설문조사로 이동"):
            st.session_state.page = 'survey1'
            st.rerun()

# --- 설문조사 1 (게임 피드백) ---
elif st.session_state.page == 'survey1':
    st.title("📝 설문조사 (1/2)")
    st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

    q1 = st.radio("1. 게임이 재미있었나요?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("2. 난이도는 어땠나요?", ["매우 쉬움", "쉬움", "보통", "어려움"])

    if st.button("다음으로"):
        st.session_state['survey_q1'] = q1
        st.session_state['survey_q2'] = q2
        st.session_state.page = 'survey2'
        st.rerun()

# --- 설문조사 2 (도박 관련 인식) ---
elif st.session_state.page == 'survey2':
    st.title("📝 설문조사 (2/2) - 도박 관련")

    q3 = st.radio("3. 이 게임은 도박과 관련 있다고 생각하나요?", ["매우 관련 있다", "관련 있다", "보통", "관련 없다"])
    q3_reason = st.text_area("   ➕ 그렇게 생각한 이유를 적어주세요.")
    q4 = st.radio("4. 이 게임이 도박 중독을 유발할 수 있다고 생각하나요?", ["매우 그렇다", "그렇다", "보통", "그렇지 않다"])
    q5 = st.radio("5. 코인이 실제 돈이었다면 결과는 달라졌을까요?", ["매우 달라졌을 것", "약간 달라졌을 것", "보통", "변화 없었을 것"])

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
            st.session_state.get('survey_q1', ''),
            st.session_state.get('survey_q2', ''),
            q3,
            q3_reason,
            q4,
            q5
        ]
        try:
            sheet.append_row(data)

            st.session_state['survey_q3'] = q3
            st.session_state['survey_q3_reason'] = q3_reason
            st.session_state['survey_q4'] = q4
            st.session_state['survey_q5'] = q5

            st.success("✅ 설문이 제출되었습니다!")
            st.session_state.page = 'submitted'
            st.rerun()
        except Exception as e:
            st.error(f"❌ 설문 제출 오류: {e}")

# --- 제출 완료 페이지 ---
elif st.session_state.page == 'submitted':
    st.title("🎉 설문 완료!")
    st.write(f"{st.session_state.user_name}님의 응답이 제출되었습니다.")

    with st.expander("🔍 제출한 응답 보기"):
        st.write(f"1. 게임이 재미있었나요? 👉 {st.session_state.get('survey_q1', '')}")
        st.write(f"2. 난이도는 어땠나요? 👉 {st.session_state.get('survey_q2', '')}")
        st.write(f"3. 도박 관련성? 👉 {st.session_state.get('survey_q3', '')}")
        st.write(f"   ➕ 이유: {st.session_state.get('survey_q3_reason', '')}")
        st.write(f"4. 도박 중독 가능성? 👉 {st.session_state.get('survey_q4', '')}")
        st.write(f"5. 코인이 실제 돈이었다면? 👉 {st.session_state.get('survey_q5', '')}")

    if st.button("🔁 다시 하기"):
        reset_game()
        st.session_state.user_name = ''
        st.session_state.class_num = 1
        st.session_state.page = 'start'
        st.rerun()
