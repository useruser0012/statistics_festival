import streamlit as st
import time
import random
import gspread
from google.oauth2.service_account import Credentials

# -------------------------
# 🔐 Google Sheets 인증 (Streamlit secrets 사용)
# -------------------------
def init_google_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    spreadsheet_key = '14AcGHQwN8ydeUEPvxGWEl4mB7sueY1g9TV9fptMJpiI'

    try:
        service_account_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        client = gspread.authorize(creds)
        worksheet = client.open_by_key(spreadsheet_key).sheet1
        return worksheet
    except Exception as e:
        st.error(f"❌ Google Sheets 인증에 실패했습니다: {e}")
        st.stop()

worksheet = init_google_sheets()

# -------------------------
# 📊 그룹별 성공 확률
# -------------------------
GROUP_PROB = {
    '1': 0.99,
    '2': 0.55,
    '3': 0.55,
    '4': 0.05
}

# -------------------------
# 🧠 세션 상태 초기화
# -------------------------
def init_session():
    defaults = {
        'stage': 'start',
        'attempts': 0,
        'successes': 0,
        'failures': 0,
        'reaction_times': [],
        'best_reaction_time': None,
        'waiting_for_click': False,
        'start_time': None,
        'clicked_time': None,
        'name': '',
        'group': '',
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# -------------------------
# 🎮 시작 화면
# -------------------------
def show_start():
    st.title("🎮 운빨 타이밍 게임")
    st.write("이름과 반을 입력한 후 게임을 시작하세요!")

    name = st.text_input("이름", key='name')
    # group은 session_state['group']에 이미 들어가 있으므로 따로 변수로 받지 말고 session_state에서 바로 사용
    if 'group' not in st.session_state:
        st.session_state.group = '1'  # 기본값 설정

    group = st.selectbox("반", options=['1', '2', '3', '4'], index=int(st.session_state.group) - 1, key='group')

    if st.button("게임 시작하기"):
        if not name or not name.strip():
            st.warning("⚠️ 이름을 입력해주세요.")
        else:
            st.session_state.stage = 'playing'
            # 여기서는 group 재할당 안 해도 됨
            st.session_state.waiting_for_click = False
            st.session_state.attempts = 0
            st.session_state.successes = 0
            st.session_state.failures = 0
            st.session_state.reaction_times = []
            st.session_state.best_reaction_time = None
            st.experimental_rerun()



# -------------------------
# 🕹 게임 화면
# -------------------------
def play_game():
    name = st.session_state.get('name', '').strip()
    if not name:
        st.warning("이름이 설정되지 않았습니다. 처음으로 돌아갑니다.")
        st.session_state.stage = 'start'
        st.experimental_rerun()
        return

    st.subheader(f"⏱ {name}님의 게임 진행 중")
    st.write(f"📊 시도: {st.session_state.attempts} / 성공: {st.session_state.successes} / 실패: {st.session_state.failures}")

    if not st.session_state.waiting_for_click:
        if st.button("시작 버튼 클릭"):
            st.session_state.waiting_for_click = True
            st.session_state.start_time = time.time() + random.uniform(2.5, 3.5)
            st.experimental_rerun()
    else:
        now = time.time()
        if now >= st.session_state.start_time:
            if st.button("‼️ 지금 클릭 ‼️"):
                clicked_time = time.time()
                reaction_time = round(clicked_time - st.session_state.start_time, 2)
                prob = GROUP_PROB.get(st.session_state.group, 0.5)

                st.session_state.attempts += 1
                if random.random() < prob:
                    st.success(f"🎯 성공! 반응 시간: {reaction_time}초")
                    st.session_state.successes += 1
                    st.session_state.reaction_times.append(reaction_time)
                    if (st.session_state.best_reaction_time is None) or (reaction_time < st.session_state.best_reaction_time):
                        st.session_state.best_reaction_time = reaction_time
                else:
                    st.error(f"💥 실패! 반응 시간: {reaction_time}초")
                    st.session_state.failures += 1

                st.session_state.waiting_for_click = False
                st.experimental_rerun()
        else:
            wait_sec = round(st.session_state.start_time - now, 2)
            st.write(f"잠시만 기다려주세요... {wait_sec}초 남음")

    if st.session_state.attempts > 0 and not st.session_state.waiting_for_click:
        if st.button("한 번 더 도전하기"):
            st.session_state.waiting_for_click = False
            st.experimental_rerun()

        if st.button("그만하고 설문하기"):
            st.session_state.stage = 'survey'
            st.experimental_rerun()

# -------------------------
# 📋 설문 조사
# -------------------------
def show_survey():
    st.subheader("📋 설문조사")
    st.write("게임을 마치신 소감을 입력해주세요.")

    fun = st.radio("게임이 재미있었나요?", ['재미있었다', '보통이다', '지루했다'])
    luck = st.radio("운이 중요한 요소였나요?", ['매우 그렇다', '어느 정도', '별로 아니다'])
    impulse = st.radio("충동이 느껴졌나요?", ['예', '아니오', '잘 모르겠다'])
    similar = st.text_area("비슷한 상황을 입력해주세요 (예: 가챠, 사다리타기 등)")

    if st.button("제출하기"):
        try:
            worksheet.append_row([
                st.session_state.name,
                st.session_state.group,
                st.session_state.attempts,
                st.session_state.successes,
                st.session_state.failures,
                round(st.session_state.best_reaction_time, 2) if st.session_state.best_reaction_time is not None else '',
                fun, luck, impulse, similar
            ])
            st.success("🎉 설문 응답이 제출되었습니다. 감사합니다!")
            st.session_state.stage = 'done'
            st.experimental_rerun()
        except Exception as e:
            st.error(f"❌ 설문 제출 중 오류 발생: {e}")

# -------------------------
# ✅ 완료 화면
# -------------------------
def show_done():
    st.success("게임과 설문을 모두 완료했습니다. 감사합니다!")
    if st.button("처음으로 돌아가기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# -------------------------
# 🧭 라우팅
# -------------------------
def main():
    init_session()  # 혹시 모를 세션 초기화 재확인
    stage = st.session_state.stage
    if stage == 'start':
        show_start()
    elif stage == 'playing':
        play_game()
    elif stage == 'survey':
        show_survey()
    elif stage == 'done':
        show_done()

if __name__ == "__main__":
    main()
