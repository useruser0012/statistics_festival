import streamlit as st
import time
import random
from datetime import datetime

# 세션 상태 초기화
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "reaction_time" not in st.session_state:
    st.session_state.reaction_time = None
if "adjusted_time" not in st.session_state:
    st.session_state.adjusted_time = None
if "success" not in st.session_state:
    st.session_state.success = None
if "clicked" not in st.session_state:
    st.session_state.clicked = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "name" not in st.session_state:
    st.session_state.name = ""
if "ban" not in st.session_state:
    st.session_state.ban = ""
if "game_count" not in st.session_state:
    st.session_state.game_count = 0
if "survey_mode" not in st.session_state:
    st.session_state.survey_mode = False

st.title("반응 속도 실험 게임")

# 이름과 반 선택
if not st.session_state.name:
    st.session_state.name = st.text_input("이름을 입력하세요.")
if not st.session_state.ban:
    st.session_state.ban = st.selectbox("반을 선택하세요.", ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

# 게임 시작 화면
if st.session_state.name and st.session_state.ban:
    if not st.session_state.game_started:
        if st.button("게임 시작"):
            st.session_state.wait_time = random.uniform(2, 5)
            st.session_state.start_delay = time.time()
            st.session_state.game_started = True
            st.session_state.clicked = False
            st.session_state.success = None
            st.session_state.reaction_time = None
            st.session_state.adjusted_time = None
            st.session_state.start_time = None
            st.rerun()
    elif not st.session_state.clicked:
        elapsed = time.time() - st.session_state.start_delay
        if elapsed >= st.session_state.wait_time:
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()
            if st.button("지금 클릭!"):
                end_time = time.time()
                reaction_time = end_time - st.session_state.start_time
                reaction_time = max(reaction_time, 0)
                st.session_state.reaction_time = reaction_time

                ban = int(st.session_state.ban)
                adjusted_time = reaction_time
                if ban in [2, 6, 10]:
                    adjusted_time *= 0.5  # 빠르게 보이도록
                elif ban in [4, 9]:
                    adjusted_time *= 2.0  # 느리게 보이도록

                st.session_state.adjusted_time = adjusted_time
                st.session_state.success = adjusted_time < 3
                st.session_state.clicked = True
                st.session_state.game_count += 1
                st.rerun()
        else:
            st.write("잠시 기다려주세요...")

    else:
        st.write(f"결과: {'성공' if st.session_state.success else '실패'}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("다시 시도하기"):
                st.session_state.game_started = False
                st.session_state.clicked = False
                st.session_state.success = None
                st.session_state.reaction_time = None
                st.session_state.adjusted_time = None
                st.session_state.start_time = None
                st.rerun()
        with col2:
            if st.button("게임 종료 후 설문조사"):
                st.session_state.survey_mode = True
                st.rerun()

# 설문조사 화면
if st.session_state.survey_mode:
    st.subheader("설문조사")
    q1 = st.radio("게임의 흥미도는 어땠나요?", options=["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("게임이 공정하다고 느꼈나요?", options=["매우 공정함", "공정함", "보통", "공정하지 않음"])
    q3 = st.radio("게임 중 충동을 느꼈나요?", options=["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
    q4 = st.text_area("비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

    if st.button("설문 제출"):
        submitted_data = {
            "이름": st.session_state.name,
            "반": st.session_state.ban,
            "반응시간": round(st.session_state.adjusted_time, 3),
            "성공여부": "성공" if st.session_state.success else "실패",
            "게임횟수": st.session_state.game_count,
            "설문_흥미도": q1,
            "설문_공정성": q2,
            "설문_충동성": q3,
            "설문_유사상황": q4,
            "제출시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Google Sheet 연동 코드 삽입 위치
        st.success("설문이 제출되었습니다. 감사합니다!")
