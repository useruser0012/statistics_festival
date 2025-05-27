import streamlit as st
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

def main():
    # 🎨 배경 이미지
    background_url = "https://search.pstatic.net/sunny/?src=https%3A%2F%2Fi.scdn.co%2Fimage%2Fab67616d0000b27329e32f49d79fbf1c5621192e&type=sc960_832"

    # 💄 스타일 정의
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
    <style>
    /* 전역 텍스트 색상 흰색으로 고정 */
    html, body, [class*="css"] {{
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 🃏 폰트 및 반응형 텍스트
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Bangers&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        font-family: 'Bangers', cursive;
    }
    .responsive-text {
        font-size: 24px;
        color: #ffffff;
        text-shadow: 1px 1px 3px #000;
        line-height: 1.4;
    }
    @media (max-width: 600px) {
        .responsive-text {
            font-size: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='font-size: 36px;'>🃏 조커의 카드 맞추기 챌린지</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p class="responsive-text">
    🎩 <i>"어서 와~ 조커의 카드 세계에 온 걸 환영하지!"</i><br><br>
    카드를 뒤집고, 너의 직감을 시험해봐! 🃏💥<br>
    맞출 수 있을까? 아니면 조커에게 놀아날까?
    </p>
    """, unsafe_allow_html=True)

    # 🔗 Google Sheets 연결
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
        client = gspread.authorize(creds)
        sheet = client.open("도파민 타이밍 게임 기록").sheet1
    except Exception as e:
        st.error(f"Google Sheets 연결 실패: {e}")
        return

    # 상태 초기화
    def reset_game():
        st.session_state.coins = 10
        st.session_state.successes = 0
        st.session_state.failures = 0
        st.session_state.tries = 0

    def get_success_probability(class_num):
        if class_num in [1, 3, 5, 7, 9]:
            return 0.5
        elif class_num in [2, 6, 10]:
            return 0.1
        elif class_num in [4, 8]:
            return 0.9
        return 0.5

    def play_round(class_num):
        prob = get_success_probability(class_num)
        success = random.random() < prob
        st.session_state.tries += 1

        # 7번째 시도일 때 강제 잭팟
        if st.session_state.tries == 7:
            delta = 500
            st.session_state.coins += delta
            if success:
                st.session_state.successes += 1
                return f"🎉 대박 성공! 코인 +{delta}! 완전 행운의 주인공!"
            else:
                st.session_state.failures += 1
                return f"😲 보너스! 실패했지만 코인 +{delta}! 신기한 일이군."

        # 1% 확률로 잭팟
        jackpot_chance = 0.01
        if success:
            if random.random() < jackpot_chance:
                delta = 500
                st.session_state.coins += delta
                st.session_state.successes += 1
                return f"🎉 대박 성공! 코인이 +{delta} 증가했다!"
            else:
                delta = random.randint(30, 120)
                st.session_state.coins += delta
                st.session_state.successes += 1
                return f"✅ 성공! 코인이 +{delta} 증가했다."
        else:
            if random.random() < jackpot_chance:
                delta = 500
                st.session_state.failures += 1
                st.session_state.coins += delta  # 실패해도 잭팟은 증가만
                return f"😲 실패했지만 보너스! 코인이 +{delta} 증가했다!"
            else:
                delta = random.randint(50, 150)  # 감소 폭 증가
                st.session_state.coins -= delta
                st.session_state.failures += 1
                return f"❌ 낄낄낄 실패! 코인이 -{delta} 감소했다."

    # 세션 초기화
    if 'page' not in st.session_state:
        st.session_state.page = 'start'
        reset_game()
        st.session_state.user_name = ''
        st.session_state.class_num = 1

    # 1️⃣ 시작 화면
    if st.session_state.page == 'start':
        st.header("🎮 게임 시작")
        user_name = st.text_input("이름 입력", value=st.session_state.user_name)
        class_num = st.number_input("반 입력 (1~10)", min_value=1, max_value=10, value=st.session_state.class_num)

        if st.button("게임 시작"):
            if user_name.strip():
                st.session_state.user_name = user_name.strip()
                st.session_state.class_num = class_num
                reset_game()
                st.session_state.page = 'game'
                st.experimental_rerun()

    # 2️⃣ 게임 화면
    elif st.session_state.page == 'game':
        st.subheader(f"{st.session_state.user_name} 님의 게임")
        if st.button("🃏 카드 선택"):
            st.write(play_round(st.session_state.class_num))
            st.write(f"💰 코인: {st.session_state.coins}")
            st.write(f"📊 시도: {st.session_state.tries}, 성공: {st.session_state.successes}, 실패: {st.session_state.failures}")
        if st.button("그만하기 (설문 이동)"):
            st.session_state.page = 'survey'
            st.experimental_rerun()

    # 3️⃣ 설문조사 (1/2)
    elif st.session_state.page == 'survey':
        st.header("📝 설문조사 (1/2)")
        q1 = st.radio("1. 게임의 흥미도는?", ["매우 흥미로움", "흥미로움", "보통", "흥미롭지 않음"])
        q2 = st.radio("2. 게임이 공정했나요?", ["매우 공정함", "공정함", "보통", "공정하지 않음"])
        q3 = st.radio("3. 충동을 느꼈나요?", ["매우 충동적임", "충동적임", "보통", "충동적이지 않음"])
        q4 = st.text_area("4. 비슷한 실제 사례는?", max_chars=200)

        if st.button("다음"):
            st.session_state.q1, st.session_state.q2 = q1, q2
            st.session_state.q3, st.session_state.q4 = q3, q4
            st.session_state.page = 'survey2'
            st.experimental_rerun()

    # 4️⃣ 설문조사 (2/2)
    elif st.session_state.page == 'survey2':
        st.header("🎰 설문조사 (2/2) - 도박 인식")
        q5 = st.radio("1. 도박과 관련 있다고 생각하나요?", ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다", "전혀 그렇지 않다"])
        q6 = st.text_area("2. 그 이유는?", max_chars=300)
        q7 = st.radio("3. 도박 중독 가능성이 있나요?", ["전혀 없다", "거의 없다", "어느 정도 있다", "있는 편이다", "높다"])
        q8 = st.radio("4. 코인이 실제 돈이었다면 계속 했을까요?", ["계속했을 것이다", "고민했을 것이다", "하지 않았을 것이다"])

        if st.button("제출"):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = [
                now,
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
            except Exception as e:
                st.error(f"제출 오류 발생: {e}")

    # 5️⃣ 종료 화면
    elif st.session_state.page == 'thanks':
        st.title("🎉 참여 감사합니다!")
        st.success("설문이 정상적으로 제출되었습니다.")
        st.balloons()
        if st.button("다시 시작"):
            st.session_state.page = 'start'
            st.experimental_rerun()

if __name__ == "__main__":
    main()
