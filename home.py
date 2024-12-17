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
st.title(":globe_with_meridians:지구촌 평화단! NGO프로젝트:globe_with_meridians:")
st.subheader(f"환영합니다, {st.session_state['NAME']}님!")

# st.subheader("메인 메뉴")

# 메뉴 버튼
st.markdown("### 메뉴 선택")
col1, col2 = st.columns(2)

with col1:
    if st.button("미션:one:"):
        st.switch_page("pages/3_미션1. 지구촌 변화와 실태 파악하기!.py")
    if st.button("미션:two:"):
        st.switch_page("pages/4_미션2. 지구의 자원을 공정하게 배분할 수 있다면.py")
    if st.button("미션:three:"):
        st.switch_page("pages/5_미션3. 지구촌 평화를 위한 특별 임무.py")        

with col2:
    if st.button("미션:four:"):
        st.switch_page("pages/6_미션4. 지구촌 평화를 위한 메시지를 전파하라!.py")
    if st.button("미션:five:"):
        st.switch_page("pages/7_미션5. 뉴스 앵커가 되어 세상을 변화시켜라!.py")
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
