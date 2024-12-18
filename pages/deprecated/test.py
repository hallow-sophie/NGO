import streamlit as st
import plotly.express as px
import pandas as pd
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")
csv_path = os.path.join(current_dir, "data", "World Population by country 2024.csv")

df = pd.read_csv(csv_path)

total_population = df["Population"].sum()
# print(total_population)
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


