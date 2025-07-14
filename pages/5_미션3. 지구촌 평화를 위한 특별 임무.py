import streamlit as st
import time


# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

st.header("미션:three: 지구촌 평화를 위한 NGO 설립하기! ❤️")

contents0 = '''
✨ **지령3: 지구촌 평화를 위한 특별 임무** ✨\n
평화 요원 여러분, 지금까지 훌륭히 미션들을 수행해왔습니다! 🙌\n
갈등 지역과 문제를 파악했고, 자원을 공정하게 배분하는 방안도 시뮬레이션했습니다.\n
이제 여러분은 한 걸음 더 나아가야 합니다.\n
**지구촌 평화를 실현할 NGO를 설립**해 여러분의 비전을 실행에 옮길 시간입니다. 🌍\n
NGO는 세계의 문제를 해결하기 위해 활동하는 비정부기구입니다.\n
이번 임무에서 여러분은 **창의적이고 실현 가능한 NGO를 설계**해야 합니다. 이름, 목표, 활동 계획까지 여러분의 아이디어로 가득 찬 NGO를 만들어주세요! 💡\n
'''
contents1 = '''
📢 **지령 내용:**\n
1️⃣ **우리 팀의 NGO 이름**을 정하고, 이 단체가 해결하려는 **문제와 목표**를 정의하세요.\n
2️⃣ NGO가 진행할 **구체적인 활동 계획**을 수립하세요.\n
(예: 어떤 지역에서 활동할지, 어떤 방식으로 문제를 해결할지, 대표 활동 예시 만들기)\n
3️⃣ 여러분의 NGO가 왜 중요한지, 어떤 변화를 가져올 수 있을지 **팀의 비전을 설명**하세요.\n
'''
contents2='''
📜 **특별 요청:**\n
NGO의 목표와 활동에는 **공정성과 인류애**가 반드시 담겨야 합니다.\n 
여러분이 설계한 NGO는 전 세계 사람들에게 희망을 전달하게 될 것입니다. 💖\n
'''
contents3='''
🤝 **추가 지령:**\n
다른 팀의 의견도 참고하며 **피드백과 협업**을 통해 NGO를 더욱 발전시키세요!\n
여러분의 창의적인 아이디어가 지구촌 평화의 열쇠가 될 것입니다.\n
평화 요원들의 열정적인 활약을 기대합니다! ✨🕊️\n
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

st.write(contents3)
st.write("")
st.write("")
st.markdown("---")

# 마크다운 링크
st.subheader("단체명을 클릭해 계획서 페이지로 이동하세요!")

col1, col2 = st.columns(2)
with col1:
    st.link_button(":one: **RNC**(Refugee Never Cry)" , "https://docs.google.com/document/d/1FqMx524LOOaz8liIZpDiIPQu5M6lAsiF7uP1wyZAZdM/edit?tab=t.0"   )
with col2:
    st.link_button(":two: **BLUE ROSE**" , "https://docs.google.com/document/d/1Q8NNEXaOGHsKV_vzAv1bmZYqDoGI3Awbn0DcCqj0Q0Y/edit?tab=t.0")
col3, col4 = st.columns(2)

with col3:
    st.link_button(":three: **HAPPY Kids**" , "https://docs.google.com/document/d/1t55IxhkYl0MPqujn2Nx_7NeBw813tVM4_q6zw9eg9yU/edit?tab=t.0")
with col4:
    st.link_button(":four: **C.F.W**(Children Free From Work)" , "https://docs.google.com/document/d/1LmuT4kT7twFWzg4QOiqVECAbs1b62bt3aX3XnoO_mzU/edit?tab=t.0")
