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

# 현재 파일 경로를 기준으로 데이터 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")

st.header("미션:one: 지구촌 변화와 실태 파악하기! :world_map:")

contents = '''
🚨 **지령1: 평화 요원 여러분!** 🚨\n
여기는 지구촌 평화단 본부입니다. 전 세계 곳곳에서 긴급한 구조 요청이 들어오고 있습니다. 난민, 빈곤, 전쟁, 의료 부족 등 지구촌의 여러 문제들이 우리를 기다리고 있어요! 🌍\n
요원들의 첫 번째 임무는 **지구촌 상황을 조사**하고, 어디에서 어떤 일이 일어나고 있는지 명확히 파악하는 것입니다. 본부가 제공하는 지도와 데이터를 활용해 **현재 상황을 시각화**하고 분석한 후 여러분의 판단을 덧붙여 **본부에 보고**하세요.\n
🎯 **지령 목표:**\n
1️⃣ 시대별 데이터를 토대로 전 세계의 갈등 지역과 문제에 대해 사태를 파악한다.\n
2️⃣ 요원들이 직접 뽑아낸 질문에 답을 하며 지구촌 갈등의 원인을 찾아낸다.\n
3️⃣ 데이터를 분석하고, 문제를 해결할 단서를 발견한다.\n
본부가 여러분에게 신뢰하는 건 바로 **공정한 판단력과 날카로운 분석 능력!** 💡\n
**준비됐나요? 그럼, 지도 위에서 활약할 시간입니다.** 🌐✨\n
'''

st.write(contents)

# Tabs 생성
tab1, tab2, tab3 = st.tabs(["기대수명 (1950년 이후, 5년 단위)","아동 사망률 (1980년, 5년 단위)","난민 수 (1990년 이후, 5년 단위)"])

with tab1:
    csv_path = os.path.join(current_dir, "data", "life-expectancy.csv")

    # CSV 데이터 로드
    data = pd.read_csv(csv_path)

    # 1950년 이후 데이터만 필터링
    data = data[data["Year"] >= 1950]

    # 5년 단위로 그룹화할 새로운 열 추가
    data["YearGroup"] = (data["Year"] // 5) * 5

    # 5년 단위 평균 계산
    grouped_data = data.groupby(["YearGroup", "Entity"], as_index=False).agg({"life": "mean"})

    # 그룹별 데이터 수 계산
    group_counts = data.groupby("YearGroup").size()

    # 데이터가 충분한 그룹만 선택 (예: 최소 10개 이상의 데이터가 있는 경우)
    min_data_threshold = 10
    valid_groups = group_counts[group_counts >= min_data_threshold].index
    filtered_grouped_data = grouped_data[grouped_data["YearGroup"].isin(valid_groups)]

    # Streamlit 앱 설정
    st.title("기대수명 (1950년 이후, 5년 단위)")

    # 유효한 연도 그룹 가져오기
    year_groups = sorted(filtered_grouped_data["YearGroup"].unique())

    if year_groups:
        # 슬라이더를 사용하여 5년 단위 그룹 선택
        selected_year_group = st.select_slider(
            "5년 단위 연도 그룹을 선택하세요",
            options=year_groups,
            format_func=lambda x: f"{x}~{x+4}"
        )

        # 선택한 5년 단위 그룹의 데이터 필터링
        filtered_data = filtered_grouped_data[filtered_grouped_data["YearGroup"] == selected_year_group]

        # GeoDataFrame 병합
        world = gpd.read_file(shapefile_path)
        merged_data = world.merge(filtered_data, left_on="ADMIN", right_on="Entity", how="left")

        # 해당 그룹의 min/max 값 계산
        if not filtered_data.empty:
            min_value = filtered_data["life"].min()
            max_value = filtered_data["life"].max()
        else:
            min_value, max_value = None, None

        # 지도 레이어 생성
        polygons = []
        for _, row in merged_data.iterrows():
            geometry = row["geometry"]
            if pd.isna(row["life"]) or min_value is None or max_value is None:  # 데이터가 없는 경우
                color = [255, 255, 255, 150]  # 흰색
            else:  # 데이터가 있는 경우
                # 정규화된 값을 사용하여 색상 설정
                normalized_value = (row["life"] - min_value) / (max_value - min_value)
                normalized_value = max(0, min(1, normalized_value))  # 범위를 0~1로 제한
                color = [
                    int((1 - normalized_value) * 255),  # Red decreases as value increases
                    int(normalized_value * 255),       # Green increases as value increases
                    0,  # Blue remains constant
                    150,  # Transparency
                ]
            if geometry.geom_type == "Polygon":
                polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "life": row["life"]})
            elif geometry.geom_type == "MultiPolygon":
                for poly in geometry.geoms:
                    polygons.append({"polygon": list(poly.exterior.coords), "color": color, "life": row["life"]})

        # Pydeck 레이어 추가
        map_layers = [
            pdk.Layer(
                "PolygonLayer",
                data=polygons,
                get_polygon="polygon",
                get_fill_color="color",
                get_line_color="[200, 200, 200, 255]" if pd.isna(row["life"]) else "[255, 255, 255, 255]",
                line_width_min_pixels=1,
                pickable=True,
            )
        ]

        # Pydeck 지도 초기 상태
        view_state = pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=1.5,
            min_zoom=0.5,
            max_zoom=10,
        )

        # Pydeck 차트 생성
        deck = pdk.Deck(
            layers=map_layers,
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/light-v9",
        )

        st.pydeck_chart(deck)

        # 선택된 연도 및 정보 표시
        st.caption(f"선택된 5년 단위 연도 그룹: {selected_year_group}~{selected_year_group+4}")
        if min_value is not None and max_value is not None: 
            st.caption(f"최소 기대수명: {min_value:.2f}세, 최대 기대수명: {max_value:.2f}세")
        else:
            st.caption("선택한 연도의 데이터가 없습니다.")

        # 색상 범례 추가
        st.markdown("### 색상 범례")
        if min_value is not None and max_value is not None:
            st.text(f"🟢 높은 기대수명 (최대값) {max_value:.2f}세")
            st.text(f"🟡 중간 기대수명")
            st.text(f"🔴 낮은 기대수명 (최소값) {min_value:.2f}세")
    else:
        st.warning("유효한 데이터가 있는 연도 그룹이 없습니다.")

with tab2:
    csv_path = os.path.join(current_dir, "data", "child-mortality-igme.csv")

    # CSV 데이터 로드
    data = pd.read_csv(csv_path)

    # 1950년 이후 데이터만 필터링
    data = data[data["Year"] >= 1980]

    # 5년 단위로 그룹화할 새로운 열 추가
    data["YearGroup"] = (data["Year"] // 5) * 5

    # 5년 단위 평균 계산
    grouped_data = data.groupby(["YearGroup", "Entity"], as_index=False).agg({"mortality": "mean"})

    # 그룹별 데이터 수 계산
    group_counts = data.groupby("YearGroup").size()

    # 데이터가 충분한 그룹만 선택 (예: 최소 10개 이상의 데이터가 있는 경우)
    min_data_threshold = 10
    valid_groups = group_counts[group_counts >= min_data_threshold].index
    filtered_grouped_data = grouped_data[grouped_data["YearGroup"].isin(valid_groups)]

    # Streamlit 앱 설정
    st.title("아동 사망률 (1980년, 5년 단위)")

    # 유효한 연도 그룹 가져오기
    year_groups = sorted(filtered_grouped_data["YearGroup"].unique())

    if year_groups:
        # 슬라이더를 사용하여 5년 단위 그룹 선택
        selected_year_group = st.select_slider(
            "5년 단위 연도 그룹을 선택하세요",
            options=year_groups,
            format_func=lambda x: f"{x}~{x+4}"
        )

        # 선택한 5년 단위 그룹의 데이터 필터링
        filtered_data = filtered_grouped_data[filtered_grouped_data["YearGroup"] == selected_year_group]

        # GeoDataFrame 병합
        world = gpd.read_file(shapefile_path)
        merged_data = world.merge(filtered_data, left_on="ADMIN", right_on="Entity", how="left")

        # 절대값 기준 정규화 설정 (0~40%)
        min_value, max_value = 0, 40

        # 지도 레이어 생성
        polygons = []
        for _, row in merged_data.iterrows():
            geometry = row["geometry"]
            mortality = row["mortality"]

            if pd.isna(mortality):  # 데이터가 없는 경우
                color = [255, 255, 255, 150]  # 흰색
            else:  # 데이터가 있는 경우
                # 절대값 기준 정규화 (0~40%)
                normalized_value = (mortality - min_value) / (max_value - min_value)
                normalized_value = max(0, min(1, normalized_value))  # 범위를 0~1로 제한
                color = [
                    int(normalized_value * 255),        # Red increases as value increases
                    int((1 - normalized_value) * 255),  # Green decreases as value increases
                    0,  # Blue remains constant
                    150,  # Transparency
                ]

            if geometry.geom_type == "Polygon":
                polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "mortality": mortality})
            elif geometry.geom_type == "MultiPolygon":
                for poly in geometry.geoms:
                    polygons.append({"polygon": list(poly.exterior.coords), "color": color, "mortality": mortality})

        # Pydeck 레이어 추가
        map_layers = [
            pdk.Layer(
                "PolygonLayer",
                data=polygons,
                get_polygon="polygon",
                get_fill_color="color",
                get_line_color="[200, 200, 200, 255]" if pd.isna(row["mortality"]) else "[255, 255, 255, 255]",
                line_width_min_pixels=1,
                pickable=True,
            )
        ]

        # Pydeck 지도 초기 상태
        view_state = pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=1.5,
            min_zoom=0.5,
            max_zoom=10,
        )

        # Pydeck 차트 생성
        deck = pdk.Deck(
            layers=map_layers,
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/light-v9",
        )

        st.pydeck_chart(deck)

        # 선택된 연도 및 정보 표시
        st.caption(f"선택된 5년 단위 연도 그룹: {selected_year_group}~{selected_year_group+4}")
        st.caption("사망률 범위: 0%~40% 기준으로 색상 표시")

        # 색상 범례 추가
        st.markdown("### 색상 범례")
        st.text("🟢 초록색: 낮은 사망률 (0%)")
        st.text("🟡 노란색: 중간 사망률 (~20%)")
        st.text("🔴 빨간색: 높은 사망률 (40%)")
    else:
        st.warning("유효한 데이터가 있는 연도 그룹이 없습니다.")

# 세 번째 Tab: 1990년 이후 5년 단위 난민 수
with tab3:
    csv_path = os.path.join(current_dir, "data", "refugee.csv")
    
    # CSV 데이터 로드
    data = pd.read_csv(csv_path)
    data = data[data["Year"] >= 1990]  # 1990년 이후 데이터 필터링
    data["YearGroup"] = (data["Year"] // 5) * 5  # 5년 단위 그룹화
    grouped_data = data.groupby(["YearGroup", "Entity"], as_index=False).agg({"refugee": "mean"})
    year_groups = sorted(grouped_data["YearGroup"].unique())
    
    st.title("난민 수 (1990년 이후, 5년 단위)")
    if year_groups:
        selected_year_group = st.select_slider(
            "5년 단위 연도 그룹을 선택하세요",
            options=year_groups,
            format_func=lambda x: f"{x}~{x+4}",
            key="select_slider_tab1"  # 고유 키 추가
        )
        
        # 데이터 필터링 및 지도 생성
        filtered_data = grouped_data[grouped_data["YearGroup"] == selected_year_group]
        world = gpd.read_file(shapefile_path)
        merged_data = world.merge(filtered_data, left_on="ADMIN", right_on="Entity", how="left")
        min_value, max_value = 0, 1_000_000
        
        polygons = []
        for _, row in merged_data.iterrows():
            geometry = row["geometry"]
            refugee_count = row["refugee"]
            if pd.isna(refugee_count):
                color = [255, 255, 255, 150]
            else:
                normalized_value = (refugee_count - min_value) / (max_value - min_value)
                normalized_value = max(0, min(1, normalized_value))
                color = [int(normalized_value * 255), int((1 - normalized_value) * 255), 0, 150]
            if geometry.geom_type == "Polygon":
                polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "refugee": refugee_count})
            elif geometry.geom_type == "MultiPolygon":
                for poly in geometry.geoms:
                    polygons.append({"polygon": list(poly.exterior.coords), "color": color, "refugee": refugee_count})
        
        map_layers = [
            pdk.Layer(
                "PolygonLayer",
                data=polygons,
                get_polygon="polygon",
                get_fill_color="color",
                get_line_color="[200, 200, 200, 255]",
                line_width_min_pixels=1,
                pickable=True,
            )
        ]
        
        view_state = pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=1.5,
            min_zoom=0.5,
            max_zoom=10,
        )

        # Pydeck 차트 생성
        deck = pdk.Deck(
            layers=map_layers,
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/light-v9",
        )

        st.pydeck_chart(deck)

        # 선택된 연도 및 정보 표시
        st.caption(f"선택된 5년 단위 연도 그룹: {selected_year_group}~{selected_year_group+4}")
        st.caption("난민 수 범위: 0~1,000,000 기준으로 색상 표시")

        # 색상 범례 추가
        st.markdown("### 색상 범례")
        st.text("🟢 초록색: 낮은 난민 수 (0)")
        st.text("🟡 노란색: 중간 난민 수 (~500,000)")
        st.text("🔴 빨간색: 높은 난민 수 (1,000,000+)")
    else:
        st.warning("유효한 데이터가 있는 연도 그룹이 없습니다.")