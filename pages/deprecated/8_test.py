import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

if "ID" not in st.session_state or st.session_state['ID'] == None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")


# Streamlit 앱
st.title("Streamlit to Google Sheets")
myid = st.session_state['ID']
conn = st.connection("gsheets", type=GSheetsConnection)

# 문제 목록
questions = [
    "1. 좋아하는 색깔은 무엇인가요?",
    "2. 가장 좋아하는 음식은 무엇인가요?",
    "3. 미래에 어떤 직업을 갖고 싶나요?"
]

# 사용자 입력 폼
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
        existing_data = conn.read(worksheet="Sheet1", ttl="10m")
        
        # Step 2: 새로운 데이터 준비
        new_data = pd.DataFrame(
            [[myid] + list(answers.values())],  # ID와 답변을 하나의 리스트로 병합
            columns=["ID"] + questions  # 열 이름 설정
        )
        
        # Step 3: 기존 데이터와 새 데이터를 병합 (pd.concat 사용)
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        
        # Step 4: 병합된 데이터를 Google Sheets에 업데이트
        conn.update(
            worksheet="Sheet1",  # 업데이트할 워크시트 이름
            data=updated_data,  # 병합된 전체 데이터
        )
        
        st.success("답변이 성공적으로 저장되었습니다!")
    else:
        st.error("모든 질문에 답변을 작성해주세요!")

# Google Sheets 데이터 읽기 및 표시
st.header("📊 Google Sheets 데이터")
df = conn.read(worksheet="Sheet1", ttl="1s")
st.dataframe(df)
