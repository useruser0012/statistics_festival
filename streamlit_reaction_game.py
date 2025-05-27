import streamlit as st
import random
import datetime
import time
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

    # 카드 이미지 리스트
    card_shine_images = [
        "https://w7.pngwing.com/pngs/552/466/png-transparent-jokerz-computer-icons-playing-card-clown-joker-heroes-fictional-character-joker.png",
        "https://w7.pngwing.com/pngs/658/87/png-transparent-black-and-gray-ace-card-united-states-playing-card-company-card-game-bicycle-plum-metal-plate-game-king-plate.png",
        "https://w7.pngwing.com/pngs/279/765/png-transparent-ace-of-spade-playing-card-ace-of-spades-standard-52-card-deck-card-game-ace-card-game-emblem-king.png",
        "https://w7.pngwing.com/pngs/902/280/png-transparent-ace-of-spades-playing-card-ace-of-hearts-spades-game-angle-king.png",
        "https://w7.pngwing.com/pngs/154/969/png-transparent-ace-of-clubs-playing-card-ace-of-spades-playing-card-espadas-ace-card-game-heroes-monochrome.png",
        "https://w7.pngwing.com/pngs/252/807/png-transparent-card-joker-harley-quinn.png",
        "https://w7.pngwing.com/pngs/733/974/png-transparent-joker-emoji-playing-card-unicode-game-card-game-heroes-text.png",
        "https://w7.pngwing.com/pngs/286/715/png-transparent-poker-playing-card-ace-of-spades-jack-joker-white-heroes-text.png",
        "https://w7.pngwing.com/pngs/344/854/png-transparent-playing-card-four-card-poker-joker-standard-52-card-deck-three-card-poker-spade-game-angle-heroes.png",
        "https://w7.pngwing.com/pngs/741/485/png-transparent-playing-card-card-game-cult-film-poker-joker-game-heroes-logo.png",
        "https://w7.pngwing.com/pngs/800/372/png-transparent-joker-playing-card-graphy-card-game-joker-king-heroes-photography.png",
        "https://w7.pngwing.com/pngs/531/586/png-transparent-joker-bicycle-playing-cards-united-states-playing-card-company-card-game-joker-king-heroes-text.png",
        "https://w7.pngwing.com/pngs/244/185/png-transparent-playing-card-card-game-ace-of-spades-joker-joker.png",
        "https://w7.pngwing.com/pngs/296/229/png-transparent-joker-playing-card-batman-text-messaging-black-card-white-mammal-heroes.png"
    ]

    # 상태 초기화 함수
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

        # 7번째 시도일 때 강제 잭팟 (코인 증가만)
        if st.session_state.tries == 7:
            delta = 500
            st.session_state.coins += delta
            if success:
                st.session_state.successes += 1
                return f"🎉 대박 성공! 코인이 +{delta} 증가했군! 운이 좋으시네~"
            else:
                st.session_state.failures += 1
                return f"🎉 대박 보너스! 코인이 +{delta} 증가했다! 자네는 행운의 여신과 함께하나?"

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
                return f"✅ 성공했군! 코인이 +{delta} 증가했다."
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
            placeholder = st.empty()
            shine_img = random.choice(card_shine_images)
            with placeholder.container():
                st.image(shine_img, width=150)
                time.sleep(0.5)
            placeholder.empty()

            # 승패 결과
            result_msg = play_round(st.session_state.class_num)
            st.success(result_msg)

            # 코인 및 통계 출력
            st.markdown(f"💰 현재 코인: **{st.session_state.coins}**")
            st.markdown(f"🎯 성공 횟수: **{st.session_state.successes}**  ❌ 실패 횟수: **{st.session_state.failures}**  총 시도: **{st.session_state.tries}**")

            # 기록 저장 (구글 시트)
            try:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sheet.append_row([
                    now,
                    st.session_state.user_name,
                    st.session_state.class_num,
                    st.session_state.coins,
                    st.session_state.successes,
                    st.session_state.failures,
                    st.session_state.tries,
                    result_msg
                ])
            except Exception as e:
                st.error(f"기록 저장 실패: {e}")

        if st.button("게임 초기화"):
            reset_game()
            st.success("게임이 초기화되었습니다!")

        if st.button("처음으로 돌아가기"):
            st.session_state.page = 'start'
            st.experimental_rerun()

    # 3️⃣ 예외 및 기타
    else:
        st.error("알 수 없는 페이지입니다. 새로고침 후 다시 시도하세요.")

if __name__ == "__main__":
    main()
