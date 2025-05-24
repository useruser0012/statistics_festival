import streamlit as st
import time
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

# -- Google Sheets 연동 설정 --
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_file = "path_to_your_credentials.json"  # 구글 서비스 계정 키 json 경로
credentials = Credentials.from_service_account_file(json_file, scopes=scope)
gc = gspread.authorize(credentials)

sheet_url = "https://docs.google.com/spreadsheets/d/your_sheet_id/edit#gid=0"
sheet = gc.open_by_url(sheet_url).sheet1

# -- 초기 상태 설정 --
if 'game_in_progress' not in st.session_state:
    st.session_state.game_in_progress = False
if 'tries' not in st.session_state:
    st.session_state.tries = 0
if 'successes' not in st.session_state:
    st.session_state.successes = 0
if 'failures' not in st.session_state:
    st.session_state.failures = 0
if 'coins' not in st.session_state:
    st.session_state.coins = 10
if 'waiting_for_click' not in st.session_state:
    st.session_state.waiting_for_click = False
if 'click_ready' not in st.session_state:
    st.session_state.click_ready = False
if 'show_survey' not in st.session_state:
    st.session_state.show_survey = False
if 'show_survey_form' not in st.session_state:
    st.session_state.show_survey_form = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'class_num' not in st.session_state:
    st.session_state.class_num = ""

# -- 사용자 정보 입력 --
st.title("반응 시간 게임 및 설문조사")

if not st.session_state.game_in_progress and not st.session_state.show_survey_form:
    st.session_state.user_name = st.text_input("이름을 입력하세요", st.session_state.user_name)
    st.session_state.class_num = st.text_input("반을 숫자로 입력하세요 (예: 2, 4, 9 등)", st.session_state.class_num)

# -- 반에 따른 반응시간 조작 비율 설정 --
def get_time_factor(class_num_str):
    try:
        c = int(class_num_str)
    except:
        return 1.0
    if c in [2, 6, 10]:
        return 0.8  # 빠르게 조작
    elif c in [4, 9]:
        return 1.3  # 느리게 조작
    else:
        return 1.0  # 기본

time_factor = get_time_factor(st.session_state.class_num)

def calculate_failure_coin_loss(tries):
    # 예: 시도 횟수 따라 코인 감소 증가 가능
    return 1  # 단순히 1코인 차감

def start_trial():
    st.session_state.tries += 1
    st.session_state.waiting_for_click = True
    st.session_state.click_ready = False
    st.session_state.start_time = 0

def trigger_click_ready():
    st.session_state.click_ready = True
    st.session_state.start_time = time.time()

def stop_game():
    st.session_state.game_in_progress = False
    st.session_state.waiting_for_click = False
    st.session_state.click_ready = False

# -- 게임 시작 버튼 --
if not st.session_state.game_in_progress and not st.session_state.show_survey_form:
    if st.button("게임 시작"):
        if st.session_state.user_name.strip() == "" or st.session_state.class_num.strip() == "":
            st.warning("이름과 반을 모두 입력해주세요.")
        else:
            st.session_state.game_in_progress = True
            st.session_state.tries = 0
            st.session_state.successes = 0
            st.session_state.failures = 0
            st.session_state.coins = 10
            start_trial()

# -- 게임 진행 중 --
if st.session_state.game_in_progress:

    st.markdown(f"**총 도전 횟수:** {st.session_state.tries}  |  **성공:** {st.session_state.successes}  |  **실패:** {st.session_state.failures}  |  **코인:** {st.session_state.coins}")

    if st.session_state.waiting_for_click:
        if not st.session_state.click_ready:
            with st.spinner("잠시 기다리세요..."):
                time.sleep(random.uniform(1.0, 3.0))
            trigger_click_ready()

        if st.button("지금 클릭!"):
            reaction_time = time.time() - st.session_state.start_time
            reaction_time *= time_factor

            if reaction_time < 0.1:
                st.warning("너무 빨리 클릭하셨습니다! 실패 처리.")
                st.session_state.failures += 1
                st.session_state.coins -= calculate_failure_coin_loss(st.session_state.tries)
            else:
                if reaction_time < 3.0:
                    st.success(f"성공! 반응 시간: {reaction_time:.2f}초")
                    st.session_state.successes += 1
                    st.session_state.coins += random.randint(30, 100)
                else:
                    st.error(f"실패... 반응 시간: {reaction_time:.2f}초")
                    st.session_state.failures += 1
                    st.session_state.coins -= calculate_failure_coin_loss(st.session_state.tries)

            st.session_state.waiting_for_click = False
            st.session_state.click_ready = False
    else:
        if st.button("다음 시도 시작"):
            start_trial()

    if st.button("게임 종료"):
        stop_game()
        st.session_state.show_survey = True

# -- 게임 종료 후 결과 및 설문조사 버튼 --
if not st.session_state.game_in_progress and st.session_state.tries > 0 and not st.session_state.show_survey_form:
    st.subheader("게임 결과")
    st.write(f"총 시도: {st.session_state.tries}")
    st.write(f"성공: {st.session_state.successes}")
    st.write(f"실패: {st.session_state.failures}")
    st.write(f"코인: {st.session_state.coins}")

    if st.session_state.show_survey:
        if st.button("게임 종료 후 설문조사"):
            st.session_state.show_survey = False
            st.session_state.show_survey_form = True

# -- 설문조사 폼 --
if st.session_state.show_survey_form:
    st.subheader("설문조사")
    st.write("설문조사에 참여해주셔서 감사합니다!")

    q1 = st.radio("게임의 흥미도는 어땠나요?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
    q2 = st.radio("게임이 공정하다고 느꼈나요?", ["매우 공정함", "공정함", "보통", "공정하지 않음"])
    q3 = st.radio("게임 중 충동을 느꼈나요?", ["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
    q4 = st.text_area("비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

    if st.button("설문 제출"):
        if st.session_state.user_name.strip() == "":
            st.warning("이름을 입력해 주세요.")
        else:
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
            try:
                sheet.append_row(values)
                st.success("설문이 성공적으로 제출되었습니다!")
                st.session_state.show_survey_form = False
            except Exception as e:
                st.error(f"설문 제출 실패: {e}")

            sheet.append_row(values)
            st.success("설문이 성공적으로 제출되었습니다!")
        except Exception as e:
            st.error(f"설문 제출 실패: {e}")
