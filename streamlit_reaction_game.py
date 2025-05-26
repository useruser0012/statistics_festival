import streamlit as st
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

# 구글 스프레드시트 연결
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("도파민 타이밍 게임 기록").sheet1

# 게임 상태 초기화 함수
def reset_game():
    st.session_state.coins = 10
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.tries = 0

# 성공 확률 함수
def get_success_probability(class_num):
    if class_num in [1, 3, 5, 7, 9]:
        return 0.5
    elif class_num in [2, 6, 10]:
        return 0.2
    elif class_num in [4, 8]:
        return 0.9
    else:
        return 0.5

# 게임 진행 함수
def play_round(class_num):
    prob = get_success_probability(class_num)
    success_flag = random.random() < prob
    coin_change = random.randint(30, 120)
    if success_flag:
        st.session_state.coins += coin_change
        st.session_state.successes += 1
        message = f"✅ 성공! 코인이 +{coin_c전 코인: {st.session_state.coins}")
    st.write(f"도전 횟수: {st.session_state.tries}, 성공: {st.session_state.successes}, 실패: {st.session_state.failures}")

    if st.button("카드 선택 (1/2 확률 게임)"):
        result_message = play_round(st.session_state.class_num)
        st.write(result_message)
        st.write(f"현재 코인: {st.session_state.coins}")

    if st.button("그만하기 (게임 종료 및 설문조사)"):
        st.session_state.page = 'survey'
        st.rerun()

# 3. 1차 설문조사
elif st.session_state.page == 'survey':
    if st.session_state.user_name.strip() == "":
        st.error("사용자 이름이 없습니다. 다시 시작해 주세요.")
        st.session_state.page = 'start'
        st.stop()

    st.title("📝 설문조사 (1/2)")
    st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

    st.session_state.q1 = st.radio("1. 게임의 흥미도는 어땠나요?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    st.session_state.q2 = st.radio("2. 게임이 공정하다고 느꼈나요?", ["매우 공정함", "공정함", "보통", "공정하지 않음"])
    st.session_state.q3 = st.radio("3. 게임 중 충동을 느꼈나요?", ["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
    st.session_state.q4 = st.text_area("4. 비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

    if st.button("다음 (2/2 설문으로 이동)"):
        st.session_state.page = 'survey2'
        st.rerun()

# 4. 2차 설문조사 (도박 관련)
elif st.session_state.page == 'survey2':
    st.title("🎰 설문조사 (2/2) - 도박 관련")

    st.session_state.q5 = st.radio("1. 이번 게임이 도박과 관련이 있다고 생각하나요?", 
                                   ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다", "전혀 그렇지 않다"])
    st.session_state.q6 = st.text_area("2. 그렇게 생각한 이유는 무엇인가요?", max_chars=300)
    st.session_state.q7 = st.radio("3. 본인은 도박 중독 가능성이 있다고 생각하나요?", 
                                   ["전혀 없다", "거의 없다", "어느 정도 있다", "있는 편이다", "높다"])
    st.session_state.q8 = st.radio("4. 이번 게임의 코인이 실제 돈이었다면, 이 게임을 계속했을 것 같나요?", 
                                   ["계속했을 것이다", "고민했을 것이다", "하지 않았을 것이다"])

    if st.button("설문 최종 제출"):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [
            now_str,
            st.session_state.user_name,
            st.session_state.class_num,
            st.session_state.tries,
            st.session_state.successes,
            st.session_state.failures,
            st.session_state.coins,
            st.session_state.q1,
            st.session_state.q2,
            st.session_state.q3,
            st.session_state.q4,
            st.session_state.q5,
            st.session_state.q6,
            st.session_state.q7,
            st.session_state.q8
        ]
        try:
            sheet.append_row(data)
            st.session_state.page = 'thanks'
            st.rerun()
        except Exception as e:
            st.error(f"❌ 설문 제출 중 오류 발생: {e}")

# 5. 설문 완료 페이지
elif st.session_state.page == 'thanks':
    st.title("🎉 설문 완료")
    st.success("설문에 참여해 주셔서 감사합니다! 🙏") 
