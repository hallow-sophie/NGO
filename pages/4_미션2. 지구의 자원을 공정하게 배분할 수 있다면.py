import streamlit as st
import os
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st
import time

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

st.header("미션:two: 지구의 자원을 공정하게 분배할 수 있다면?:face_with_monocle:")

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
    st.subheader(f"현재 문제 번호: {current_question_index}")
    st.write("문제를 맞춰보세요!")
    # 현재 문제 가져오기
    current_question = questions[current_question_index - 1]

    # 문제 출력 (일반 문제)
    st.write(f"문제: {current_question['question']}")
    st.latex(r"㉠ \cdot \left(\frac{㉡}{\text{㉢}}\right)")
    user_answer1 = st.text_input("㉠ 을 입력하세요.")
    user_answer2 = st.text_input("㉡ 을 입력하세요.")
    user_answer3 = st.text_input("㉢ 을 입력하세요.")
    
    answer = [None] * 3
    answer[0] = "몰"
    answer[1] = "라"
    answer[2] = "요"

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
    st.subheader(f"현재 문제 번호: {current_question_index}")
    # st.title("나라별 인구 수 입력 문제")
    st.write("각 나라의 인구 수(백만 단위)를 입력하세요.")
    st.latex(r"\text{나라별 인구 수를 입력하여 데이터를 제출하세요.}")

    correct_data = [
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1]
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
    if st.button("제출"):
        is_correct = True  # 전체 정답 여부
        incorrect_countries = []  # 틀린 나라를 저장

        # 모든 값을 정답 데이터와 비교
        for i in range(4):
            for j in range(5):
                input_value = st.session_state["population_data"][i][j]
                correct_value = correct_data[i][j]
                # 오차 범위 계산 (1%)
                if abs(input_value - correct_value) / correct_value > 0.01:
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

elif current_question_index == 3:
    st.subheader(f"현재 문제 번호: {current_question_index}")
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
    if st.button("다음 문제로"):
        st.session_state["score"] += 1
        st.session_state["current_question"] += 1  # 다음 문제로 이동
        st.rerun()




elif current_question_index == 4:
    st.subheader(f"현재 문제 번호: {current_question_index}")    
    st.write("입력하신 인구수로 가상의 자원 100을 비례배분한 결과 입니다.")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")
    csv_path = os.path.join(current_dir, "data", "World Population by country 2024.csv")

    # CSV 데이터 로드
    data = pd.read_csv(csv_path)
    # 지도 표시에 필요한 컬러 값 계산 (인구수 기반)
    min_population = data["Population"].min()
    max_population = data["Population"].max()
    
    world = gpd.read_file(shapefile_path)
    # GeoDataFrame과 데이터 병합
    merged_data = world.merge(data, left_on="ADMIN", right_on="country", how="left")

    # 인구수 범위 설정
    min_value = 0
    max_value = data["Population"].max() if "Population" in data.columns else 1_000_000

    # 지도 레이어 생성
    polygons = []
    for _, row in merged_data.iterrows():
        geometry = row["geometry"]
        population = row["Population"]

        # 색상 계산
        if pd.isna(population):  # 데이터가 없는 경우
            color = [255, 255, 255, 150]  # 흰색
        else:
            # 정규화 (0 ~ max_value)
            normalized_value = (population - min_value) / (max_value - min_value)
            normalized_value = max(0, min(1, normalized_value))  # 범위 제한
            color = [
                int((1 - normalized_value) * 255),  # 빨간색 강도 (낮은 값일수록 강해짐)
                int(normalized_value * 255),       # 초록색 강도 (높은 값일수록 강해짐)
                0,                                 # 파란색 강도
                150,                               # 투명도
            ]

        # 폴리곤 데이터 추가
        if geometry is not None:
            if geometry.geom_type == "Polygon":
                polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "Population": population})
            elif geometry.geom_type == "MultiPolygon":
                for poly in geometry.geoms:
                    polygons.append({"polygon": list(poly.exterior.coords), "color": color, "Population": population})

    # PyDeck 레이어 추가
    map_layers = [
        pdk.Layer(
            "PolygonLayer",
            data=polygons,
            get_polygon="polygon",
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
        )
    ]

    # PyDeck 초기 상태
    view_state = pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1.5,
        min_zoom=0.5,
        max_zoom=10,
    )

    # PyDeck 차트 생성
    deck = pdk.Deck(
        layers=map_layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip={"text": "인구 수: {population}"}
    )

    # Streamlit UI
    st.title("국가별 인구 지도")
    st.pydeck_chart(deck)

    # 색상 범례 추가
    st.markdown("### 색상 범례")
    st.text("🟢 초록색: 높은 비율 (최소)")
    st.text("🟡 노란색: 중간 비율 ")
    st.text("🔴 빨간색: 낮은 비율 (최대)")

    st.write("Q1. 인구수대로 자원을 배분한다면 어느 나라가 풍족하고, 어느 나라가 적게 가져가나요?")
    st.write("Q2. 현재 전 세계 결과와 비교하면 어떤 차이가 있을까요?")
    st.write("Q3. 인구 수대로 자원을 배분하는 것은 \"공정\" 한 방법일까요?")


elif current_question_index == 5:
    # 퀴즈 완료 화면
    st.title("퀴즈 완료!")
    st.write(f"축하합니다! 점수: {st.session_state['score']} / {len(questions)}")
    if st.button("다시 시작하기"):
        st.session_state["current_question"] = 1
        st.session_state["score"] = 0
        st.rerun()
