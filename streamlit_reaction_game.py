import streamlit as st
import random
import time
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- 구글 스프레드시트 연결 설정 ---
SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '구글스프레드시트ID를_여기에_입력하세요'

creds = Credentials.from_service_account_file(service_account.json, scopes=SCOPE)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# --- 클래스별 성공률, 시간 조작 비율 설정 ---
class_settings = {
    1: {"success_rate": 0.6, "time_factor": 1.0},    # 1반: 0.6, 기본 시간
    2: {"success_rate": 0.99, "time_factor": 0.8},   # 2반: 0.99, 시간 빠름
    3: {"success_rate": 0.6, "time_factor": 1.0},    # 3반: 0.6, 기본 시간
    4: {"success_rate": 0.05, "time_factor": 1.3},   # 4반: 0.05, 시간 느림
}

# --- 코인 초기값 및 증감 범위 ---
COIN_START = 50
SUCCESS_COIN_MIN = 5
SUCCESS_COIN_MAX = 100
FAIL_COIN_MIN = 10
FAIL_COIN_MAX = 130

# --- 실패 멘트 리스트 ---
FAIL_MESSAGES = [
    "실패! 단 **{:.2f}초 차이**로 놓쳤어요! 정말 아깝네요!",
    "실패! 목표 시간보다 **{:.2f}초 늦었어요. 조금만 빨랐다면 성공이었는데요!",
    "실패! 거의 성공할 뻔했어요. 다음엔 꼭 할 수 있어요!"
]

st.title("🎮 반별 조작된 반응속도 게임 + 설문조사")

# --- 최고 기록 저장용 세션 변수 ---
if "best_score" not in st.session_state:
    st.session_state.best_score = 0

# --- 게임 상태 초기화 ---
if "coins" not in st.session_state:
    st.session_state.coins = COIN_START
if "tries" not in st.session_state:
    st.session_state.tries = 0
if "successes" not in st.session_state:
    st.session_state.successes = 0
if "failures" not in st.session_state:
    st.session_state.failures = 0
if "game_running" not in st.session_state:
    st.session_state.game_running = False
if "results" not in st.session_state:
    st.session_state.results = []

# --- 이름과 반 입력 ---
with st.form("user_form"):
    user_name = st.text_input("이름을 입력하세요", max_chars=20)
    class_num = st.selectbox("반을 선택하세요 (1~4반)", options=[1, 2, 3, 4])
    submitted = st.form_submit_button("게임 시작")

if submitted:
    if not user_name.strip():
        st.error("이름을 입력해야 합니다!")
    else:
        st.session_state.user_name = user_name.strip()
        st.session_state.class_num = class_num
        st.session_state.game_running = True
        st.session_state.coins = COIN_START
        st.session_state.tries = 0
        st.session_state.successes = 0
        st.session_state.failures = 0
        st.session_state.results = []
        st.experimental_rerun()

if not st.session_state.get("game_running", False):
    st.info("이름과 반을 입력하고 게임을 시작하세요.")
    st.stop()

# --- 게임 진행 ---

st.write(f"안녕하세요, **{st.session_state.user_name}**님! 반: **{st.session_state.class_num}반**")
st.write(f"현재 코인: 💰 **{st.session_state.coins}**")
st.write(f"시도: {st.session_state.tries}회 | 성공: {st.session_state.successes}회 | 실패: {st.session_state.failures}회")
st.write(f"최고 기록: {st.session_state.best_score} 코인")

success_rate = class_settings[st.session_state.class_num]["success_rate"]
time_factor = class_settings[st.session_state.class_num]["time_factor"]

# --- 도박 빠짐 패턴: 2,3반만 조작된 딜레이 시뮬레이션 ---
def is_success_with_pattern(try_num):
    if st.session_state.class_num not in [2, 3]:
        return random.random() < success_rate
    # 2,3반: 초반은 성공 유도, 중반부터 실패 증가 후 끝 무렵 성공 소량
    total = 30  # 예시 시도 총 횟수 (필요하면 더 키울 수 있음)
    if try_num < total * 0.3:
        return True
    elif try_num < total * 0.7:
        return random.random() < 0.4  # 실패 높임
    elif try_num < total * 0.85:
        return False  # 연속 실패
    else:
        return random.random() < 0.3  # 끝에 약간 성공

# --- 실패 멘트 랜덤 ---
def get_fail_message(diff_sec):
    msg_template = random.choice(FAIL_MESSAGES)
    return msg_template.format(diff_sec)

# --- 게임 시도 시작 ---
if st.button("시도하기 (반응 속도 맞추기)"):
    st.session_state.tries += 1

    # 반응 시간 측정 시뮬레이션 (실제는 키 입력 등으로 구현 가능)
    base_time = random.uniform(0.5, 2.0)  # 예: 0.5~2초 반응
    adjusted_time = base_time * time_factor

    # 성공 여부 판단
    success = is_success_with_pattern(st.session_state.tries)
    coin_change = 0

    if success:
        # 성공: 코인 증가 (5~100 사이 랜덤)
        coin_change = random.randint(SUCCESS_COIN_MIN, SUCCESS_COIN_MAX)
        st.session_state.successes += 1
        st.session_state.coins += coin_change
        st.success(f"🎉 성공! 반응 시간: {adjusted_time:.2f}초 (조작됨)")
        st.info(f"💰 코인 +{coin_change} 획득! 현재 코인: {st.session_state.coins}")
    else:
        # 실패: 코인 감소 (10~130 사이 랜덤)
        coin_change = -random.randint(FAIL_COIN_MIN, FAIL_COIN_MAX)
        st.session_state.failures += 1
        st.session_state.coins += coin_change
        # 실패 시간 차이 랜덤 (0.01~0.15초)
        diff_sec = random.uniform(0.01, 0.15)
        fail_msg = get_fail_message(diff_sec)
        st.error(f"❌ {fail_msg}")
        st.info(f"💰 코인 {coin_change} 감소. 현재 코인: {st.session_state.coins}")

    # 최고 기록 갱신
    if st.session_state.coins > st.session_state.best_score:
        st.session_state.best_score = st.session_state.coins

    # 시도 결과 저장 (시간, 성공 여부, 코인 증감량)
    st.session_state.results.append({
        "try": st.session_state.tries,
        "success": success,
        "coin_change": coin_change,
        "reaction_time": adjusted_time,
        "timestamp": datetime.datetime.now().isoformat()
    })

# --- 그만하기 & 설문조사 ---

if st.button("게임 종료 및 설문조사"):
    st.session_state.game_running = False

    st.write("## 설문조사")

    with st.form("survey_form"):
        q1 = st.radio("게임의 흥미도는 어땠나요?", options=["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
        q2 = st.radio("게임이 공정하다고 느꼈나요?", options=["매우 공정함", "공정함", "보통", "공정하지 않음"])
        q3 = st.radio("게임 중 충동을 느꼈나요?", options=["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
        q4 = st.text_area("비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

        survey_submitted = st.form_submit_button("결과 제출 및 저장")

        if survey_submitted:
            # 구글 스프레드시트에 저장
            try:
                values = [
                    st.session_state.user_name,
                    st.session_state.class_num,
                    st.session_state.tries,
                    st.session_state.successes,
                    st.session_state.failures,
                    st.session_state.coins,
                    str(datetime.datetime.now()),
                    q1, q2, q3, q4
                ]
                request = sheet.values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range="시트1!A1",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [values]},
                )
                request.execute()
                st.success("데이터가 성공적으로 저장되었습니다! 감사합니다.")
            except Exception as e:
                st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

            st.stop()

# --- 최고 기록 보여주기 ---
st.write("---")
st.write(f"현재 최고 기록: 💰 **{st.session_state.best_score}** 코인")

pip install google-api-python-client
