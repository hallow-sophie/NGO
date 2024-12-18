import streamlit as st
import os
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st
import plotly.express as px
import time
from streamlit_gsheets import GSheetsConnection

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

st.header("미션:two: 지구의 자원을 공정하게 분배할 수 있다면?:face_with_monocle:")

contents0 = '''
🕊️ **지령2: 공정한 배분을 위한 전략회의** 🕊️\n
평화 요원 여러분! 훌륭하게 미션 1을 완료했군요. 👏\n
여러분 덕분에 전 세계의 갈등 지역과 문제들을 명확히 파악할 수 있었습니다. 그러나 여기서 끝이 아닙니다!\n
이번엔 전 세계로부터 도착한 자원을 **공정하게 분배하는 작업**이 필요합니다. 🌍⛽\n
지구촌 곳곳에서 필요한 자원이 다르고, 사람마다 필요의 정도가 다르기 때문에, **어떻게 배분해야 가장 공정할지** 여러분의 전략적 사고가 중요합니다.\n
'''
contents1 = '''
💼 **지령 내용:**\n
1️⃣ 본부가 제공하는 **자원의 총량 100을 전세계 인구 수에 비례하여 배분**해보는 ‘자원 배분 시뮬레이션’을 돌려보세요.\n
2️⃣ **세계 각 나라의 인구 수를 조사**하고 요구하는 비율을 입력해 **비례적으로 자원을 분배**하세요.\n
3️⃣ 시뮬레이션 도구를 활용해 시각화된 배분 결과를 토대로 **결과를 분석**하세요.\n
4️⃣ 배분 결과가 공정한 지, 공정한 자원 배분은 어떻게 이루어질 수 있을지 **여러분의 판단**을 덧붙여 본부에 보고하세요.\n
'''

contents2 = '''
🚨 **긴급 공지:**\n
배분이 불공정하면 갈등이 더 커질 수도 있습니다. 🆘\n
하지만 요원들의 **공정성과 인류애**가 담긴 배분이라면, 더 나은 미래를 만들 수 있을 거예요! 💖\n
이제 **자원의 공정한 배분**을 위해 본부를 도와주세요. 여러분의 능력을 믿습니다! 🌟\n
'''

st.write(contents0)
st.write("")
st.write("")

st.write(contents1)
st.write("")
st.write("")

st.write(contents2)
st.write("")
st.write("")
st.markdown("---")

# 문제와 정답 정의
questions = [
    {"question": "만약 100만큼의 자원을 각 나라의 인구수의 비로 자원을 배분한다면 어떻게 계산할까요?", "answer": "해당 나라 인구 수"},  # 문제 1
    {"question": r"a \cdot \left(\frac{b}{c}\right)", "answer": None},  # 문제 2 (수학 문제)
]

countries = [
    ["미국", "캐나다", "멕시코", "브라질", "아르헨티나"],
    ["영국", "독일", "프랑스", "이탈리아", "스페인"],
    ["중국", "인도", "일본", "한국", "베트남"],
    ["남아프리카공화국", "나이지리아", "이집트", "케냐", "에티오피아"]
]

# 세션 상태 초기화
if "current_question" not in st.session_state:
    st.session_state["current_question"] = 1
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "population_data" not in st.session_state:
    st.session_state["population_data"] = [[0 for _ in range(5)] for _ in range(4)]  # 4x5 초기화

# 현재 문제 번호 가져오기
current_question_index = st.session_state["current_question"]

# 문제 풀이 UI
if current_question_index == 1:
    st.subheader(f"📍문제 : {current_question_index}")
    st.write("문제를 맞춰보세요!")
    # 현재 문제 가져오기
    current_question = questions[current_question_index - 1]

    # 문제 출력 (일반 문제)
    st.write(f"문제: {current_question['question']}")
    st.latex(r"㉠ \cdot \left(\frac{㉡}{\text{㉢}}\right)")
    user_answer1 = st.text_input("㉠ 을 입력하세요.")
    user_answer2 = st.text_input("㉡ 을 입력하세요.")
    user_answer3 = st.text_input("㉢ 을 입력하세요.")
    
    st.write("**보기**")
    st.write("모든 나라 인구수 합")
    st.write("해당 나라 인구수")
    st.write("100")

    answer = [None] * 3
    answer[0] = "100"
    answer[1] = "해당 나라 인구수"
    answer[2] = "모든 나라 인구수 합"

    # 제출 버튼
    if st.button("제출"):
        if (user_answer1.strip().lower() == answer[0].strip().lower() 
            and user_answer2.strip().lower() == answer[1].strip().lower() 
            and user_answer3.strip().lower() == answer[2].strip().lower()):
            st.success("정답입니다!")
            st.session_state["score"] += 1
            st.session_state["current_question"] += 1  # 다음 문제로 이동
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도해보세요.")

elif current_question_index == 2:
    st.subheader(f"📍문제 : {current_question_index}")
    # st.title("나라별 인구 수 입력 문제")
    st.write("각 나라의 인구 수(천 단위)를 입력하세요.")
    st.latex(r"\text{나라별 인구 수를 입력하여 데이터를 제출하세요.}")

    correct_data = [
        [345427, 39742, 130861, 211999, 45696],
        [69138, 84552, 66549, 59343, 47911],
        [1419321, 1450936, 123753, 51751, 100988],
        [64007, 232679, 116538, 56433, 132060]
    ]

    # 4x5 입력 필드 생성
    for i in range(4):  # 행 반복
        cols = st.columns(5)  # 5개의 열 생성
        for j in range(5):  # 열 반복
            with cols[j]:
                st.session_state["population_data"][i][j] = st.number_input(
                    label=countries[i][j],
                    value=st.session_state["population_data"][i][j],  # 초기값 유지
                    min_value=0,
                    # step=1,
                    key=f"input_{i}_{j}"  # 고유 키 설정
                )

    # 입력된 데이터 출력
    # st.table(st.session_state["population_data"])

    # 제출 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("제출"):
            is_correct = True  # 전체 정답 여부
            incorrect_countries = []  # 틀린 나라를 저장

            # 모든 값을 정답 데이터와 비교
            for i in range(4):
                for j in range(5):
                    input_value = st.session_state["population_data"][i][j]
                    correct_value = correct_data[i][j]
                    # 오차 범위 계산 (5%)
                    if abs(input_value - correct_value) / correct_value > 0.05:
                        is_correct = False
                        incorrect_countries.append(countries[i][j])

            # 결과 출력
            if is_correct:
                st.success("모든 입력값이 정답입니다!")
                st.session_state["score"] += 1
                st.session_state["current_question"] += 1  # 다음 화면으로 이동
                st.rerun()
            else:
                st.error("입력된 값 중 일부가 정답이 아닙니다.")
                st.write("틀린 나라 목록:")
                st.write(", ".join(incorrect_countries))
    with col2:
        if st.button("전 단계로"):
            st.session_state["current_question"] -= 1
            st.session_state["score"] -= 1
            st.rerun()            

elif current_question_index == 3:
    st.subheader(f"📍문제 : {current_question_index}")
    st.write("직접 계산해 봅시다.")
    # st.title(f"현재 문제 번호: {current_question_index}")

    # 현재 문제 가져오기
    left_col, right_col = st.columns(2)

    # 문제 출력 (일반 문제)
    with left_col:
        st.latex(r"㉠ \cdot \left(\frac{㉡}{\text{㉢}}\right)")
        user_answer1 = st.number_input("㉠ 값을 입력하세요:", value=1, key="input_a")
        user_answer2 = st.number_input("㉡ 값을 입력하세요:", value=1, key="input_b")
        user_answer3 = st.number_input("㉢ 값을 입력하세요 (0 제외):", value=1, key="input_c")
    with right_col:
        st.write("결과:")
        try:
            # 계산 결과
            if user_answer3 == 0:
                st.error("㉢ 값은 0이 될 수 없습니다.")
            else:
                result = user_answer1 * (user_answer2 / user_answer3)
                st.success(f"계산 결과: {result:.2f}")
        except Exception as e:
            st.error(f"계산 중 오류가 발생했습니다: {e}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다음 문제로"):
            st.session_state["score"] += 1
            st.session_state["current_question"] += 1  # 다음 문제로 이동
            st.rerun()
    with col2:
        if st.button("전 단계로"):
            st.session_state["current_question"] -= 1
            st.session_state["score"] -= 1
            st.rerun()



elif current_question_index == 4:
    myid = st.session_state['ID']
    conn = st.connection("gsheets", type=GSheetsConnection)

    st.subheader(f"📍문제 : {current_question_index}")    
    st.write("입력하신 인구수로 가상의 자원 100을 비례배분한 결과 입니다.")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")
    csv_path = os.path.join(current_dir, "data", "World Population by country 2024.csv")

    df = pd.read_csv(csv_path)

    total_population = df["Population"].sum()
    df["Percentage"] = (df["Population"] / total_population) * 100
    df["자원 배분 결과"] = df["Percentage"]

    fig = px.treemap(
        df,
        path=["country"],  # 계층 구조 설정
        values="자원 배분 결과",  # 크기 기준
        color="자원 배분 결과",  # 색상 기준
        hover_data=["자원 배분 결과"],
        color_continuous_scale="Viridis",  # 색상 스케일
        title="자원 배분 Tree Map"
    )

    # Label과 툴팁 설정
    fig.update_traces(
        textinfo="label+text",  # Tree Map에 나라 이름과 백분율 표시
        texttemplate="<b>%{label}</b><br>%{customdata[0]}%",  # Tree Map 내부 텍스트: 나라 이름 + 백분율
        hovertemplate="<b>나라 :</b> %{label}<br>" +       # Hover 시 나라 이름
                    "<b>자원 배분:</b> %{customdata[0]}%"  # Hover 시 백분율
    )

    st.plotly_chart(fig)

    questions = [
        ":male-detective: 인구수대로 자원을 배분한다면 어느 나라가 풍족하고, 어느 나라가 적게 가져가나요?",
        ":female-detective: 현재 전 세계 결과와 비교하면 어떤 차이가 있을까요?",
        ":male-detective: 인구 수대로 자원을 배분하는 것은 \"공정\" 한 방법일까요?",
        ":female-detective: 공정하게 자원을 배분하는 방법은 무엇일까요?"
    ]
    st.write("")
    st.header("**💡요원들이여, 분석하라!**")\

    with st.form("data_input_form"):
        answers = {}
        for question in questions:
            answers[question] = st.text_input(question)  # 각 질문에 대한 답변 입력
        submit_button = st.form_submit_button("제출")

    # Google Sheets에 데이터 추가
    if submit_button:
        # 모든 답변이 작성되었는지 확인
        if all(answers.values()):
            # Step 1: 기존 데이터 읽기
            existing_data = conn.read(worksheet="Mission2-1", ttl="1s")
            
            # Step 2: 새로운 데이터 준비
            new_data = pd.DataFrame(
                [[myid] + list(answers.values())],  # ID와 답변을 하나의 리스트로 병합
                columns=["ID"] + questions  # 열 이름 설정
            )
            
            # Step 3: 기존 데이터와 새 데이터를 병합 (pd.concat 사용)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            
            # Step 4: 병합된 데이터를 Google Sheets에 업데이트
            conn.update(
                worksheet="Mission2-1",  # 업데이트할 워크시트 이름
                data=updated_data,  # 병합된 전체 데이터
            )
            
            st.success("답변이 성공적으로 저장되었습니다!")
        else:
            st.error("모든 질문에 답변을 작성해주세요!")

    # Google Sheets 데이터 읽기 및 표시
    st.header("📊 Google Sheets 데이터")
    df = conn.read(worksheet="Mission2-1", ttl="1s")
    st.dataframe(df)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다음 문제로"):
            st.session_state["score"] += 1
            st.session_state["current_question"] += 1  # 다음 문제로 이동
            st.rerun()
    with col2:
        if st.button("전 단계로"):
            st.session_state["current_question"] -= 1
            st.session_state["score"] -= 1
            st.rerun()


elif current_question_index == 5:
    # 퀴즈 완료 화면
    st.title("퀴즈 완료!")
    st.write(f"축하합니다! 점수: {st.session_state['score']} / 4")
    if st.button("다시 시작하기"):
        st.session_state["current_question"] = 1
        st.session_state["score"] = 0
        st.rerun()
