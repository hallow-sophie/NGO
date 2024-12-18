import streamlit as st
import pandas as pd
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="로그인", page_icon="🔒", layout="wide")
st.title("🦸‍♀️ 또바기 6기_6성4이다반_로그인 페이지 🦸‍♂️")
st.image(os.path.join(current_dir,"images", '2024_로고.jpg'), width=500)
data = pd.read_csv("members.csv")
data["PW"] = data["PW"].astype(str)

with st.form("login_form"):
    ID = st.text_input("ID", placeholder="아이디를 입력하세요")
    PW = st.text_input("Password", type="password", placeholder="비밀번호를 입력하세요")
    submit_button = st.form_submit_button("로그인")

if submit_button:
    if not ID or not PW:
        st.warning("ID와 비밀번호를 모두 입력해주세요.")
    else:
        user = data[(data["ID"] == ID) & (data["PW"] == str(PW))]
        if not user.empty:
            # 사용자 이름 가져오기
            user_name = user.iloc[0]["NAME"]  # 첫 번째 행의 NAME 필드 가져오기
            st.success(f"{user_name}님 환영합니다!")  # NAME 필드를 환영 메시지에 사용
            st.session_state["ID"] = ID
            st.session_state["NAME"] = user_name

            progress_text = "로그인 중입니다."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)
            my_bar.empty()
            st.switch_page("home.py")
        else:
            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
