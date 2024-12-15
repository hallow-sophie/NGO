import streamlit as st
import time

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] == None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

# 사용자 이름 표시
st.set_page_config(page_title="홈", page_icon="🏠")
st.title(f"환영합니다, {st.session_state['NAME']}님!")
st.subheader("메인 메뉴")

# 메뉴 버튼
st.markdown("### 메뉴 선택")
col1, col2 = st.columns(2)

with col1:
    if st.button("기대수명"):
        st.switch_page("pages/3_기대수명.py")
    if st.button("아동사망률"):
        st.switch_page("pages/4_아동사망률.py")
    if st.button("난민수"):
        st.switch_page("pages/5_난민수.py")        

with col2:
    if st.button("NGO설립계획서"):
        st.switch_page("pages/6_NGO설립계획서.py")
    if st.button("인터뷰하기"):
        st.switch_page("pages/7_인터뷰하기.py")
    if st.button("로그아웃"):
        st.session_state.pop("ID", None)
        st.success("로그아웃되었습니다. 로그인 페이지로 이동합니다.")
        st.switch_page("pages/2_login.py")

# 알림 섹션
st.markdown("### 알림")
st.info("새로운 알림이 없습니다.")

# Footer
st.markdown("---")
st.caption("© 2024 Your App. All rights reserved.")
