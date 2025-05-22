import streamlit as st
import random
import time
import gspread
from google.oauth2.service_account import Credentials

# 구글 시트 인증 설정 (oauth2client → google-auth)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)

# 구글 시트 열기
sheet = client.open("도파민 타이밍 게임 기록").sheet1
survey_sheet = sheet  # 그대로 사용해도 됩니다


# 초기 설정
st.set_page_config(page_title="반응 속도 게임", layout="centered")

# 세션 상태 초기화
def init_state():
    keys_defaults = {
        'stage': 'start',
        'reaction_times': [],
        'name': '',
        'classroom': '',
        'waiting_for_click': False,
        'start_time': 0.0,
        'attempts': 0,
        'successes': 0,
        'failures': 0,
        'best_reaction_time': None,
        'trigger_time': 0.0,
        'survey_done': False,
    }
    for key, default in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

# 반별 성공률 설정
success_rate_by_class = {
    "1반": 0.99,
    "2반": 0.6,
    "3반": 0.6,
    "4반": 0.05
}

# 반별 반응 시간 조작 함수
def manipulate_reaction_time(classroom, reaction_time):
    rate = success_rate_by_class.get(classroom, 1.0)
    rnd = random.random()
    if classroom == "1반":
        if rnd > rate:
            return max(0, reaction_time + random.uniform(0.4, 1.0))
        else:
            return max(0, reaction_time - random.uniform(0.2, 0.5))
    elif classroom in ["2반", "3반"]:
        if rnd > rate:
            return max(0, reaction_time + random.uniform(0.3, 0.7))
        else:
            return max(0, reaction_time - random.uniform(0.1, 0.3))
    elif classroom == "4반":
        if rnd < rate:
            return max(0, reaction_time - random.uniform(0.2, 0.5))
        else:
            return max(0, reaction_time + random.uniform(0.4, 1.0))
    return reaction_time

# 게임 초기 화면
def show_start():
    st.title("🎮 반응 속도 게임")
    st.markdown("""
    ### 👋 환영합니다!
    이 게임은 여러분의 반응 속도를 테스트합니다. 버튼이 초록색으로 바뀌면 **즉시 클릭**하세요!
    이름과 반을 입력한 후 게임을 시작하세요.
    """)

    st.session_state.name = st.text_input("이름을 입력하세요:", st.session_state.name)
    st.session_state.classroom = st.selectbox("반을 선택하세요:", ["1반", "2반", "3반", "4반"], index=0 if st.session_state.classroom == '' else ["1반", "2반", "3반", "4반"].index(st.session_state.classroom))

    if st.button("게임 시작하기"):
        if not st.session_state.name or not st.session_state.name.strip():
            st.warning("⚠️ 이름을 입력해주세요.")
        else:
            st.session_state.stage = 'playing'
            st.session_state.waiting_for_click = False
            st.session_state.attempts = 0
            st.session_state.successes = 0
            st.session_state.failures = 0
            st.session_state.reaction_times = []
            st.session_state.best_reaction_time = None
            st.session_state.survey_done = False
            st.experimental_rerun()

# 게임 화면
def show_game():
    st.title("⏱️ 반응 속도 측정 중")
    if not st.session_state.waiting_for_click:
        wait_time = random.uniform(2, 5)
        st.session_state.waiting_for_click = True
        st.session_state.trigger_time = time.time() + wait_time
        st.info("곧 버튼이 초록색으로 바뀝니다. 준비하세요!")
    else:
        current_time = time.time()
        if current_time >= st.session_state.trigger_time:
            if st.button("지금 클릭!", key='active'):
                raw_reaction_time = current_time - st.session_state.trigger_time
                reaction_time = manipulate_reaction_time(st.session_state.classroom, raw_reaction_time)
                st.session_state.reaction_times.append(reaction_time)
                st.session_state.successes += 1
                if st.session_state.best_reaction_time is None or reaction_time < st.session_state.best_reaction_time:
                    st.session_state.best_reaction_time = reaction_time
                st.session_state.attempts += 1
                st.session_state.waiting_for_click = False
                st.experimental_rerun()
            else:
                st.success("버튼을 클릭하세요!")
        else:
            if st.button("지금 클릭!", key='early_click'):
                st.session_state.failures += 1
                st.session_state.attempts += 1
                st.session_state.waiting_for_click = False
                st.warning("너무 빨랐어요! 다시 시도하세요.")
                st.experimental_rerun()

    if st.session_state.attempts >= 4:
        st.session_state.stage = 'result'
        st.experimental_rerun()

# 설문 조사 화면
def show_survey():
    st.title("📝 간단한 설문조사")
    st.markdown("게임을 마친 후의 소감을 알려주세요!")

    q1 = st.radio("게임이 재미있었나요?", ["매우 그렇다", "그렇다", "보통이다", "아니다"])
    q2 = st.radio("공정한 게임이라고 느꼈나요?", ["매우 그렇다", "그렇다", "보통이다", "아니다"])
    q3 = st.radio("게임 중 충동을 느꼈나요? (예: 너무 빨리 누르고 싶은 욕구 등)", ["매우 그렇다", "그렇다", "보통이다", "아니다"])
    q4 = st.text_area("이와 비슷한 충동이나 심리를 유발하는 상황에는 어떤 것이 있다고 생각하나요?")

    if st.button("설문 제출"):
        row = [st.session_state.name, st.session_state.classroom, q1, q2, q3, q4]
        survey_sheet.append_row(row)
        st.session_state.survey_done = True
        st.success("설문이 제출되었습니다. 감사합니다!")
        st.balloons()

# 결과 화면
def show_result():
    st.title("🏁 결과 보기")
    name = st.session_state.name
    classroom = st.session_state.classroom
    reaction_times = st.session_state.reaction_times
    avg_time = sum(reaction_times) / len(reaction_times) if reaction_times else 0
    best_time = st.session_state.best_reaction_time

    st.markdown(f"""
    ## 📋 {name}님의 결과
    - 반: {classroom}
    - 시도 횟수: {st.session_state.attempts}
    - 성공 횟수: {st.session_state.successes}
    - 실패 횟수: {st.session_state.failures}
    - 평균 반응 시간: {avg_time:.3f}초
    - 최고 반응 시간: {best_time:.3f}초
    """)

    row = [name, classroom, st.session_state.attempts, st.session_state.successes, st.session_state.failures, f"{avg_time:.3f}", f"{best_time:.3f}"]
    sheet.append_row(row)

    if not st.session_state.survey_done:
        if st.button("설문 작성하기"):
            st.session_state.stage = 'survey'
            st.experimental_rerun()
    else:
        if st.button("다시 시작하기"):
            st.session_state.stage = 'start'
            st.experimental_rerun()

# 메인 함수
def main():
    init_state()
    if st.session_state.stage == 'start':
        show_start()
    elif st.session_state.stage == 'playing':
        show_game()
    elif st.session_state.stage == 'result':
        show_result()
    elif st.session_state.stage == 'survey':
        show_survey()

if __name__ == "__main__":
    main()
import os
import streamlit as st
