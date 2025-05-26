import streamlit as st
import time
import random

# --- 세션 상태 초기화 ---
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'start'
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'class_num' not in st.session_state:
        st.session_state.class_num = 1
    if 'tries' not in st.session_state:
        st.session_state.tries = 0
    if 'successes' not in st.session_state:
        st.session_state.successes = 0
    if 'failures' not in st.session_state:
        st.session_state.failures = 0
    if 'coins' not in st.session_state:
        st.session_state.coins = 10
    if 'state' not in st.session_state:
        st.session_state.state = 'ready'  # 'ready', 'waiting', 'reaction'
    if 'reaction_start_time' not in st.session_state:
        st.session_state.reaction_start_time = 0
    if 'result_message' not in st.session_state:
        st.session_state.result_message = ""
    if 'success_rate' not in st.session_state:
        st.session_state.success_rate = 0.5  # 기본 성공률 50%

init_session_state()

# --- 반별 성공률 설정 함수 ---
def set_success_rate(class_num):
    if class_num == 1:
        return 0.99
    elif class_num in [2,3]:
        return 0.6
    elif class_num == 4:
        return 0.05
    else:
        return 0.5

# --- 페이지별 UI 및 로직 ---
if st.session_state.page == 'start':
    st.title("도파민 타이밍 게임")
    name_input = st.text_input("이름을 입력하세요")
    class_input = st.selectbox("반을 선택하세요", options=[1,2,3,4])

    if st.button("게임 시작"):
        if name_input.strip() == "":
            st.warning("이름을 입력해 주세요.")
        else:
            st.session_state.user_name = name_input.strip()
            st.session_state.class_num = class_input
            st.session_state.success_rate = set_success_rate(class_input)
            # 초기 게임 상태 초기화
            st.session_state.tries = 0
            st.session_state.successes = 0
            st.session_state.failures = 0
            st.session_state.coins = 10
            st.session_state.state = 'ready'
            st.session_state.result_message = ""
            st.session_state.page = 'game'
            st.experimental_rerun()  # 페이지 이동 즉시 반영
            st.stop()

elif st.session_state.page == 'game':
    st.header(f"도파민 타이밍 게임 진행 중\n{st.session_state.user_name}님, {st.session_state.class_num}반 게임 중입니다.")
    st.write(f"총 시도: {st.session_state.tries} | 성공: {st.session_state.successes} | 실패: {st.session_state.failures} | 코인: {st.session_state.coins}")
    st.write(st.session_state.result_message)

    if st.session_state.state == 'ready':
        if st.button("준비 완료, 시작!"):
            wait_time = random.uniform(2.0, 5.0)  # 2~5초 랜덤 대기
            st.session_state.state = 'waiting'
            st.session_state.wait_until = time.time() + wait_time
            st.experimental_rerun()
            st.stop()

    elif st.session_state.state == 'waiting':
        now = time.time()
        if now >= st.session_state.wait_until:
            st.session_state.state = 'reaction'
            st.session_state.reaction_start_time = now
            st.experimental_rerun()
            st.stop()
        else:
            st.write("잠시만 기다려주세요...")
            time.sleep(0.1)
            st.experimental_rerun()
            st.stop()

    elif st.session_state.state == 'reaction':
        if st.button("클릭!"):
            reaction_time = time.time() - st.session_state.reaction_start_time
            st.session_state.tries += 1

            # 성공률 조작
            success_chance = st.session_state.success_rate
            random_val = random.random()

            if random_val <= success_chance:
                # 성공 처리
                st.session_state.successes += 1
                st.session_state.coins += 1
                st.session_state.result_message = f"성공! 반응시간: {reaction_time:.3f}초"
            else:
                # 실패 처리
                st.session_state.failures += 1
                st.session_state.coins = max(0, st.session_state.coins - 1)
                st.session_state.result_message = f"실패! 반응시간: {reaction_time:.3f}초"

            st.session_state.state = 'ready'
            st.experimental_rerun()
            st.stop()

    if st.button("게임 종료 및 처음으로"):
        st.session_state.page = 'start'
        st.experimental_rerun()
        st.stop()
