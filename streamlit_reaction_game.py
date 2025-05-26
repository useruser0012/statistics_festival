import streamlit as st
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

# 구글 API 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("도파민 타이밍 게임 기록").sheet1

# 반별 성공 확률 설정
class_success_rate = {
    1: 0.6,
    2: 0.2,
    3: 0.6,
    4: 0.9,
    5: 0.6,
    6: 0.2,
    7: 0.6,
    8: 0.9,
    9: 0.6,
    10: 0.2,
}

def reset_game():
    st.session_state.tries = 0
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.coins = 10
    st.session_state.result = ""
    st.session_state.page = "start"

# 세션 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1
if 'tries' not in st.session_state:
    reset_game()

if st.session_state.page == "start":
    st.title("도파민 타이밍 게임")
    st.session_state.user_name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
    st.session_state.class_num = st.selectbox("반을 선택하세요", list(range(1, 11)), index=st.session_state.class_num-1)
    if st.button("게임 시작"):
        if not st.session_state.user_name.strip():
            st.warning("이름을 입력해 주세요.")
        else:
            reset_game()
            st.session_state.page = "game"
            st.experimental_rerun()

elif st.session_state.page == "game":
    st.title("도파민 타이밍 게임")
    user_name = st.session_state.user_name
    class_num = st.session_state.class_num
    success_rate = class_success_rate[class_num]

    st.write(f"👤 {user_name}님 | 🏫 {class_num}반")
    st.write(f"🔁 시도: {st.session_state.tries} | ✅ 성공: {st.session_state.successes} | ❌ 실패: {st.session_state.failures} | 🪙 코인: {st.session_state.coins}")

    st.write("카드나 버튼을 선택하세요! (1/2 확률로 성공 여부 결정)")

    if st.button("카드 선택"):
        st.session_state.tries += 1

        # 성공 여부 판정 (반별 확률 적용)
        if random.random() < success_rate:
            coin_change = random.randint(30, 120)
            st.session_state.coins += coin_change
            st.session_state.successes += 1
            st.session_state.result = f"✅ 성공! 코인 {coin_change}개 획득!"
        else:
            # 실패 시 감소량은 성공 시 얻었을 코인 수만큼 감소 (성공 코인 랜덤 재생성)
            coin_loss = random.randint(30, 120)
            st.session_state.coins -= coin_loss
            st.session_state.failures += 1
            st.session_state.result = f"❌ 실패! 코인 {coin_loss}개 감소..."

        st.experimental_rerun()

    if st.session_state.result:
        st.markdown(f"### {st.session_state.result}")

    if st.button("게임 종료 후 설문조사"):
        st.session_state.page = "survey"
        st.experimental_rerun()

elif st.session_state.page == "survey":
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

        # 초기화 후 시작 페이지로 이동
        st.session_state.user_name = ""
        st.session_state.class_num = 1
        reset_game()
        st.experimental_rerun()
