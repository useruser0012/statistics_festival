import streamlit as st
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

def main():
    # 🎨 배경 이미지
    background_url = "https://search.pstatic.net/sunny/?src=https%3A%2F%2Fi.scdn.co%2Fimage%2Fab67616d0000b27329e32f49d79fbf1c5621192e&type=sc960_832"

    # 💄 스타일
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url('{background_url}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white;
    }}
    [data-testid="stAppViewContainer"] .block-container {{
        background-color: rgba(0, 0, 0, 0.7);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 0 30px rgba(255,255,255,0.3);
    }}
    h1, h2, h3 {{
        color: #ffdd00;
        text-shadow: 2px 2px 6px #000;
    }}
    button {{
        background-color: #e84118 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 12px !important;
        box-shadow: 0 0 10px #e84118 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 🃏 폰트 적용 + 반응형 CSS 추가
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Bangers&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        font-family: 'Bangers', cursive;
    }

    /* 본문 스타일 */
    .responsive-text {
        font-size: 24px;
        color: #ffffff;
        text-shadow: 1px 1px 3px #000;
        line-height: 1.4;
    }

    /* 모바일 화면에서 폰트 크기 줄이기 */
    @media (max-width: 600px) {
        .responsive-text {
            font-size: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # 🎮 타이틀 (원하는 크기로 직접 스타일링 가능)
    st.markdown("<h1 style='font-size: 36px;'>🃏 조커의 카드 맞추기 챌린지</h1>", unsafe_allow_html=True)

    # 반응형 텍스트
    st.markdown("""
    <p class="responsive-text">
    🎩 <i>"어서 와~ 조커의 카드 세계에 온 걸 환영하지!"</i><br><br>
    카드를 뒤집고, 너의 직감을 시험해봐! 🃏💥<br>
    맞출 수 있을까? 아니면 조커에게 놀아날까?
    </p>
    """, unsafe_allow_html=True)


    # 🔗 Google Sheets 연결
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("도파민 타이밍 게임 기록").sheet1

    # 🌟 게임 상태 초기화 함수
    def reset_game():
        st.session_state.coins = 10
        st.session_state.successes = 0
        st.session_state.failures = 0
        st.session_state.tries = 0

    # 🎯 성공 확률 설정
    def get_success_probability(class_num):
        if class_num in [1, 3, 5, 7, 9]:
            return 0.5
        elif class_num in [2, 6, 10]:
            return 0.1
        elif class_num in [4, 8]:
            return 0.9
        else:
            return 0.5

    # 🃏 한 판 게임
    def play_round(class_num):
        prob = get_success_probability(class_num)
        success_flag = random.random() < prob
        coin_change = random.randint(30, 120)
        st.session_state.tries += 1
        if success_flag:
            st.session_state.coins += coin_change
            st.session_state.successes += 1
            return f"✅ 성공이군! 코인이 +{coin_change} 만큼 증가했다."
        else:
            st.session_state.coins -= coin_change
            st.session_state.failures += 1
            return f"❌ 낄낄낄 실패! 코인이 -{coin_change} 만큼 감소했다."

    # 세션 초기화
    if 'page' not in st.session_state:
        st.session_state.page = 'start'
    if 'coins' not in st.session_state:
        reset_game()
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ''
    if 'class_num' not in st.session_state:
        st.session_state.class_num = 1

    # 1️⃣ 시작 페이지
    if st.session_state.page == 'start':
        st.header("🎮 게임 시작 페이지")
        user_name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
        class_num = st.number_input("반을 입력하세요 (1~10)", min_value=1, max_value=10, value=st.session_state.class_num)

        if st.button("게임 시작") and user_name.strip():
            st.session_state.user_name = user_name.strip()
            st.session_state.class_num = class_num
            reset_game()
            st.session_state.page = 'game'
            st.experimental_rerun()
            return  # 함수 내부라 가능

    # 2️⃣ 게임 페이지
    elif st.session_state.page == 'game':
        st.subheader(f"플레이어: {st.session_state.user_name} / 반: {st.session_state.class_num}")

        if st.button("🃏 카드 선택 (1/2 확률 게임)"):
            result_message = play_round(st.session_state.class_num)
            st.write(result_message)
            st.write(f"💰 현재 코인: {st.session_state.coins}")
            st.write(f"📊 도전 횟수: {st.session_state.tries}, 성공: {st.session_state.successes}, 실패: {st.session_state.failures}")
            # 스파클 애니메이션 보여주기 (예: GIF URL 사용)
            sparkle_url = "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif"
            st.image(sparkle_url, width=150)

        if st.button("그만하기 (게임 종료 및 설문조사)"):
            st.session_state.page = 'survey'
            st.experimental_rerun()
            return

    # 3️⃣ 설문 1
    elif st.session_state.page == 'survey':
        if st.session_state.user_name.strip() == "":
            st.error("사용자 이름이 없습니다. 다시 시작해 주세요.")
            st.session_state.page = 'start'
            st.experimental_rerun()
            return

        st.header("📝 설문조사 (1/2)")
        st.write(f"{st.session_state.user_name}님, 게임에 참여해 주셔서 감사합니다!")

        q1 = st.radio("1. 게임의 흥미도는 어땠나요?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
        q2 = st.radio("2. 게임이 공정하다고 느꼈나요?", ["매우 공정함", "공정함", "보통", "공정하지 않음"])
        q3 = st.radio("3. 게임 중 충동을 느꼈나요?", ["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
        q4 = st.text_area("4. 비슷한 실제 상황에는 무엇이 있다고 생각하나요?", max_chars=200)

        if st.button("다음 (2/2 설문으로 이동)"):
            st.session_state.q1 = q1
            st.session_state.q2 = q2
            st.session_state.q3 = q3
            st.session_state.q4 = q4
            st.session_state.page = 'survey2'
            st.experimental_rerun()
            return

    # 4️⃣ 설문 2
    elif st.session_state.page == 'survey2':
        st.header("🎰 설문조사 (2/2) - 도박 관련")

        q5 = st.radio("1. 이번 게임이 도박과 관련이 있다고 생각하나요?", 
                      ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다", "전혀 그렇지 않다"])
        q6 = st.text_area("2. 그렇게 생각한 이유는 무엇인가요?", max_chars=300)
        q7 = st.radio("3. 본인은 도박 중독 가능성이 있다고 생각하나요?", 
                      ["전혀 없다", "거의 없다", "어느 정도 있다", "있는 편이다", "높다"])
        q8 = st.radio("4. 이번 게임의 코인이 실제 돈이었다면, 이 게임을 계속했을 것 같나요?", 
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
                q5, q6, q7, q8
            ]
            try:
                sheet.append_row(data)
                st.session_state.page = 'thanks'
                st.experimental_rerun()
                return
            except Exception as e:
                st.error(f"❌ 설문 제출 중 오류 발생: {e}")

    # 5️⃣ 감사합니다 페이지
    elif st.session_state.page == 'thanks':
        st.title("🎉 참여 감사합니다!")
        st.success("설문이 성공적으로 제출되었습니다.")
        st.balloons()
        if st.button("처음으로 돌아가기"):
            st.session_state.page = 'start'
            st.experimental_rerun()
            return

if __name__ == "__main__":
    main()
