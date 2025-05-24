import streamlit as st
import random
import time
import datetime

import gspread
from google.oauth2.service_account import Credentials

# 구글 API 범위 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("도파민 타이밍 게임 기록").sheet1

# 클래스별 시간 조작 비율 (반응시간에 곱함)
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

# 성공 확률을 반응시간 기준으로 동적으로 계산하는 함수
# 짧은 반응시간일수록 성공 확률 높고, 길면 낮음 (예: 0.1초 이하 거의 100%, 3초 이상 거의 0%)
def get_success_probability(reaction_time):
    if reaction_time < 0.1:
        return 0.0  # 너무 빨리 누르면 실패
    elif reaction_time > 3.0:
        return 0.0  # 너무 늦으면 실패
    else:
        # 반응시간 0.1~3초 사이일 때 선형적으로 성공확률 감소
        return max(0.0, min(1.0, 1.0 - (reaction_time - 0.1) / (3.0 - 0.1)))

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
    st.session_state.game_in_progress = False
    st.session_state.waiting_for_click = False
    st.session_state.start_time = 0
    st.session_state.reaction_start_time = 0
    st.session_state.next_click_time = 0
    st.session_state.result_message = ""
    st.session_state.page = "game"  # 게임 페이지로 이동

# 페이지 초기 설정
if 'page' not in st.session_state:
    st.session_state.page = "start"  # start, game, survey

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'class_num' not in st.session_state:
    st.session_state.class_num = 1

if st.session_state.page == "start":
    st.title("도파민 타이밍 게임")
    st.session_state.user_name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
    st.session_state.class_num = st.selectbox("반을 선택하세요", list(range(1, 11)), index=st.session_state.class_num-1)
    if st.button("게임 시작"):
        if not st.session_state.user_name.strip():
            st.warning("이름을 입력해 주세요.")
        else:
            reset_game()

elif st.session_state.page == "game":
    st.title("도파민 타이밍 게임 진행 중")
    user_name = st.session_state.user_name
    class_num = st.session_state.class_num
    time_factor = class_settings[class_num]["time_factor"]

    st.write(f"{user_name}님, {class_num}반 게임 중입니다.")
    st.write(f"총 시도: {st.session_state.tries} | 성공: {st.session_state.successes} | 실패: {st.session_state.failures} | 코인: {st.session_state.coins}")

    # 게임 종료 버튼
    if st.button("게임 종료 후 설문조사"):
        st.session_state.page = "survey"

    # 결과 메시지 출력
    if st.session_state.result_message:
        st.markdown(st.session_state.result_message)

    # 게임 진행 로직
    now = time.time()

    if st.session_state.waiting_for_click:
        # '지금 클릭' 버튼 활성화 시간 지났으면 버튼 보여줌
        if now >= st.session_state.next_click_time:
            if st.button("지금 클릭!"):
                raw_reaction_time = time.time() - st.session_state.reaction_start_time
                reaction_time = raw_reaction_time * time_factor

                # 성공 확률 계산
                success_prob = get_success_probability(reaction_time)

                if reaction_time < 0.1:
                    st.warning("너무 빨리 클릭하셨습니다! 실패로 처리됩니다.")
                    st.session_state.failures += 1
                    coin_loss = calculate_failure_coin_loss(st.session_state.tries)
                    st.session_state.coins -= coin_loss
                    st.session_state.result_message = f"너무 빠른 클릭으로 실패! 코인 {coin_loss}개 손실."
                else:
                    if random.random() <= success_prob:
                        st.success("성공했습니다!")
                        st.session_state.successes += 1
                        coin_gain = random.randint(30, 100)
                        st.session_state.coins += coin_gain
                        st.session_state.result_message = f"코인 {coin_gain}개 획득!"
                    else:
                        st.error("실패했습니다.")
                        st.session_state.failures += 1
                        coin_loss = calculate_failure_coin_loss(st.session_state.tries)
                        st.session_state.coins -= coin_loss
                        st.session_state.result_message = f"코인 {coin_loss}개 손실."

                if st.session_state.coins < 0:
                    st.session_state.coins = 0

                st.session_state.waiting_for_click = False
        else:
            st.write("잠시 기다려 주세요...")

    else:
        # 다음 시도 준비 버튼
        if st.session_state.tries >= 1000:
            st.write("최대 시도 횟수에 도달했습니다.")
            st.session_state.page = "survey"
        else:
            if st.button("다음 시도 시작"):
                st.session_state.tries += 1
                st.session_state.waiting_for_click = True
                st.session_state.result_message = ""

                # 클릭할 수 있는 시간은 1~3초 뒤 랜덤으로 설정 (사용자가 버튼 기다림)
                delay = random.uniform(1.0, 3.0)
                st.session_state.next_click_time = time.time() + delay

                # 클릭 반응 시간 측정 시작 시점은 next_click_time부터
                st.session_state.reaction_start_time = st.session_state.next_click_time

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
            st.error(f"설문 제출 중 오류가 발생했습니다: {e}")

        # 초기화
        st.session_state.page = "start"
        st.session_state.user_name = ""
        st.session_state.class_num = 1
