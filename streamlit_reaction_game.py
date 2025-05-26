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

# 게임 상태 초기화 함수
def reset_game():
    st.session_state.coins = 10
    st.session_state.successes = 0
    st.session_state.failures = 0
    st.session_state.tries = 0

# 성공 확률 반환 함수
def get_success_probability(class_num):
    if class_num in [1, 3, 5, 7, 9]:
        return 0.5
    elif class_num in [2, 6, 10]:
        return 0.2
    elif class_num in [4, 8]:
        return 0.9
    else:
        return 0.5

# 게임 라운드 실행 함수
def play_round(class_num):
    prob = get_success_probability(class_num)
    success_flag = random.random() < prob
    coin_change = random.randint(30, 120)
    if success_flag:
        st.session_state.coins += coin_change
        st.session_state.successes += 1
        message = f"✅ 성공! 코인이 +{coin_change} 만큼 증가했습니다."
    else:
        st.session_state.coins -= coin_change
        st.session_state.failures += 1
        message = f"❌ 실패... 코인이 -{coin_change} 만큼 감소했습니다."
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

# 1. 게임 시작 페이지
if st.session_state.page == 'start':
    st.title("🎮 게임 시작 페이지")
    user_name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
    class_num = st.number_input("반을 입력하세요 (1~10)", min_value=1, max_value=10, step=1, value=st.session_state.class_num)
    
    if st.button("게임 시작") and user_name.strip() != "":
        st.session_state.user_name = user_name.strip()
        st.session_state.class_num = class_num
        reset_game()
        st.session_state.page = 'game'
        st.rerun()

# 2. 게임 플레이 페이지
elif st.session_state.page == 'game':
    st.title("🃏 카드 맞추기 게임")
    st.write(f"플레이어: {st.session_state.user_name} / 반: {st.session_state.class_num}")
    st.write(f"현재 코인: {st.session_state.coins}")
    st.write(f"도전 횟수: {st.session_state.tries}, 성공: {st.session_state.successes}, 실패: {st.session_state.failures}")

    if st.button("카드 선택 (1/2 확률 게임)"):
        result_message = play_round(st.session_state.class_num)
        st.write(result_message)
        st.write(f"현재 코인: {st.session_state.coins}")

    if st.button("그만하기 (게임 종료 및 설문조사)"):
        if st.session_state.user_name.strip() == "":
            st.error("사용자 이름이 비어 있습니다. 설문으로 이동할 수 없습니다.")
        else:
            st.session_state.page = 'survey'
            st.rerun()

# 3. 설문조사 페이지 (두 번째 설문)  [수정됨]
elif st.session_state.page == 'survey':
    if st.session_state.user_name.strip() == "":
        st.error("사용자 이름이 없습니다. 다시 시작해 주세요.")
        st.session_state.page = 'start'
        st.stop()

    st.title("📝 설문조사")
    st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

    q1 = st.radio("1. 게임이 재미있었나요?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("2. 난이도는 어땠나요?", ["매우 쉬움", "쉬움", "보통", "어려움"])
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
            q1,
            q2,
            q3,
            q3_reason,
            q4,
            q5
        ]
        try:
            sheet.append_row(data)

            # [수정됨] 응답 내용 저장
            st.session_state['survey_q1'] = q1
            st.session_state['survey_q2'] = q2
            st.session_state['survey_q3'] = q3
            st.session_state['survey_q3_reason'] = q3_reason
            st.session_state['survey_q4'] = q4
            st.session_state['survey_q5'] = q5

            st.success("✅ 설문이 제출되었습니다! 감사합니다.")
            st.session_state.page = 'submitted'
            st.rerun()
        except Exception as e:
            st.error(f"❌ 설문 제출 중 오류 발생: {e}")

# 4. 제출된 응답 미리보기 페이지  [수정됨]
elif st.session_state.page == 'submitted':
    st.title("🎉 설문 완료!")
    st.write(f"{st.session_state.user_name}님의 응답이 성공적으로 제출되었습니다.")

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
