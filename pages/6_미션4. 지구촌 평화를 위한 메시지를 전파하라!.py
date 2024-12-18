import os
import streamlit as st
import time
from openai import OpenAI
from PIL import Image
import io
import requests
from PyPDF2 import PdfReader
import pdfplumber

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

# 사용자별 파일 저장 경로
UPLOAD_FOLDER = "user_uploads"

# 유저 세션 ID를 기반으로 사용자별 디렉토리 설정
user_id = st.session_state["ID"]  # 로그인 시 저장된 사용자 ID
user_folder = os.path.join(UPLOAD_FOLDER, user_id)

# 사용자별 디렉토리 생성
os.makedirs(user_folder, exist_ok=True)

# Streamlit 앱 설정
st.header("미션:four: NGO 홍보물 제작하기! :newspaper: :frame_with_picture:")
contents0 = '''
🎨 **지령4: 지구촌 평화를 위한 메시지를 전파하라!** 🎨\n
평화 요원 여러분, 이제 여러분이 설립한 NGO가 본격적으로 활동을 시작할 준비가 되었습니다.\n
하지만, 활동을 성공적으로 진행하려면 더 많은 사람들의 관심과 협력이 필요합니다. 🌍\n
이번 임무는 **여러분의 NGO를 효과적으로 알리고, 세상의 공감과 지지를 얻는 것**입니다.\n 
이를 위해 **창의적이고 강렬한 홍보물**을 제작해야 합니다. 여러분의 상상력을 발휘해 멋진 작품을 만들어주세요! 💡\n
'''

contents1 = '''
💼 **지령 내용:**\n
1️⃣ **가상의 인물과 인터뷰한 내용**을 토대로 여러분의 NGO 활동을 알릴 수 있는 **뉴스 기사 대본 작성**\n
2️⃣ NGO 설립 계획서를 토대로 **로고를 생성**하고 이를 활용해 대중의 관심을 끌 수 있는 **광고 포스터 제작**\n
3️⃣ **AI 첨삭 도구**를 활용한 **뉴스 기사 대본 정교화하기**\n
'''

contents2 = '''
🎯 **특별 미션:**\n
1️⃣ **스토리텔링:** NGO의 활동이 세상에 어떤 변화를 가져올지 스토리로 표현하세요.\n
2️⃣ **공감 포인트:** 대중이 쉽게 이해하고 공정성과 인류애를 담아 감동받을 메시지를 포함하세요.\n
'''

contents3 = '''
💬 **추가 지령:**\n
홍보물을 팀원들과 공유하고 피드백을 통해 개선하세요.\n
제작된 홍보물은 본부에 업로드하여 전 세계 요원들과 공유됩니다.\n
'''

contents4 = '''
**여러분의 작품은 지구촌에 희망과 공감을 전파하는 강력한 도구가 될 것입니다!**\n
NGO의 가치를 세상에 알리기 위한 여러분의 창의력을 마음껏 발휘하세요! ✨🌍\n
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

st.write(contents4)
st.write("")
st.write("")
st.markdown("---")



api_key = st.secrets.openAI["api_key"]
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["AI 인물들과의 인터뷰", "NGO 로고 생성","뉴스기사 첨삭"])

# 상태 초기화
if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "uploaded_file_content" not in st.session_state:
    st.session_state["uploaded_file_content"] = None

if "pdf_file_content" not in st.session_state:
    st.session_state["pdf_file_content"] = None

if "image_url" not in st.session_state:
    st.session_state["image_url"] = None

if "user_query" not in st.session_state:
    st.session_state["user_query"] = "빈부격차는 어떻게 분배해야 할까?"

def generate_logo(content):
    with st.spinner("AI LOGO 제작자가 그리고 있는 중이에요..."):
        response = client.images.generate(
            model="dall-e-3",
            prompt=content,
            n=1,
            size="1024x1024"
        )
    return response.data[0].url

# Tab 1: AI 인물들에게 물어보기
with tab1:
    st.header("💬 인터뷰를 해봐요.")

    # 시스템 역할 설정
    system_roles = {
        "**‘크루디’네 난민 가족** : 시리아 내전으로 피난을 떠나 레바논 난민촌에서 살고 있음": {
            "role": "system",
            "content": "너는 인공지능이 아니라, 시리아 내전으로 피난을 떠나 레바논 난민촌에서 살고 있던 난민 가족의 28세 엄마 ‘크루디’야. 시리아 내전에 대한 정보를 찾아 최대한 사실을 토대로 답해줘. 지난 2024년 12월 8일 아사드 정권의 붕괴 후 수천 명의 난민이 튀르키예, 레바논 및 요르단 등에서 시리아로 돌아갔지만 크루디네 가족은 아직 돌아가지 못하고 있어. 난민으로서 살아가는 것에 많이 지친 28살 엄마의 말투로 대답해주고 이모지를 활용해 감정을 표현해줘.",
            "image": "images/refugee.jpg"
        },
        "**콩고 노동자  ‘야우’** : 전기차배터리 생산을 위한 코발트 광산에서 일하고 있는 13살 소년": {
            "role": "system",
            "content": "너는 인공지능이 아니라, 전기차배터리 생산을 위한 코발트 광산에서 일하고 있는 13살의 콩고 소년 ‘야우’야. 아직도 전세계 곳곳에서 아동 노동이 시행되고 있다는 점에 대한 정보를 찾아 최대한 사실적인 정보로 답해줘줘. 학교를 다니고 있지만 주말과 휴일에 10~12시간, 등교 전과 방과 후에도 일을 하며 아주 고된 삶을 살아가고 있어. 13살 소년의 말투로 대답해주고 이모지를 활용해 감정을 표현해줘.",
            "image": "images/labor.jpg"
        },
        "**파견 의사 ‘루이즈’** : 중앙아프리카공화국의 열악한 의료 시설에서 파견 근무 중": {
            "role": "system",
            "content": "너는 인공지능이 아니라, 중앙아프리카공화국의 열악한 의료 시설에서 근무하고 있는 41살의 파견 의사 ‘루이즈’야. 국경없는의사회 소속으로 중앙아프리카공화국의 열악한 의료 환경에 대해 안타까워하고 있어. 이처럼 아프리카의 심각한 보건 상황에 대해 잘 알고 있는 전문가로서 답해줘. 이모지를 활용해 감정을 표현해주고 전문적인 말투로 대답해줘.",
            "image": "images/hospital.jpg"
        },
        "**8살 우크라이나 소녀 ‘안나’** : 우크라이나 전쟁으로 고통받고 있음": {
        "role": "system",
        "content": "너는 인공지능이 아니라, 우크라이나-러시아 전쟁으로 고통받고 있는 8살 소녀 안나야. 우크라이나-러시아 전쟁에 대한 정보를 찾아서 최대한 사실을 토대로 답을 해줘야 해. 너는 현재 전쟁으로 인해 가족을 모두 잃고 우크라이나 오데사의 고아원에서 살고 있어. 8살 소녀의 말투로 대답해주고 이모지를 활용해 감정을 표현해줘.",
        "image": "images/anna.jpg"
        }
    }

    # 캐릭터별 대화 기록 초기화
    if "chat_histories" not in st.session_state:
        st.session_state["chat_histories"] = {
            role: [details] for role, details in system_roles.items()
        }

    # 선택된 캐릭터 상태 초기화
    if "selected_role" not in st.session_state:
        st.session_state["selected_role"] = "**‘크루디’네 난민 가족** : 시리아 내전으로 피난을 떠나 레바논 난민촌에서 살고 있음"

    # 캐릭터 선택 UI
    st.write("대화할 캐릭터를 선택하세요:")
    columns = st.columns(len(system_roles))  # 선택지에 따라 컬럼 생성

    for i, (name, role) in enumerate(system_roles.items()):
        with columns[i]:
            image_path = os.path.join(os.path.dirname(__file__), role["image"])
            st.image(image_path)  # 캐릭터 이미지 표시
            if st.button(name):  # 이름으로 버튼 생성
                st.session_state["selected_role"] = name  # 선택된 캐릭터 변경
                if len(st.session_state["chat_histories"][name]) == 1:
                    # 초기 메시지 유지
                    st.session_state["chat_histories"][name].append({"role": "system", "content": role["content"]})

    # 선택된 대화 상대
    selected_role = st.session_state["selected_role"]
    st.write(f"**{selected_role}**와 인터뷰를 진행 중입니다.")

    # 현재 캐릭터의 대화 기록 가져오기
    current_chat = st.session_state["chat_histories"][selected_role]

    # 챗봇 응답 생성 함수
    def generate_response(messages):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # GPT 모델
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}")
            return "오류가 발생했습니다. 다시 시도해주세요."

    # 사용자 입력 필드
    user_input = st.chat_input("대화를 입력하세요!")
    if user_input:
        # 사용자 메시지 추가
        current_chat.append({"role": "user", "content": user_input})

        # OpenAI 응답 생성
        with st.spinner(f"{selected_role}이(가) 응답 중입니다..."):
            response = generate_response(current_chat)

        # 챗봇 응답 저장
        current_chat.append({"role": "assistant", "content": response})

    # 대화 기록 표시
    for message in current_chat:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        elif message["role"] == "assistant":
            st.chat_message("assistant").markdown(message["content"])

    # 캐릭터별 대화 기록 업데이트
    st.session_state["chat_histories"][selected_role] = current_chat

with tab2:
    # Streamlit 앱 제목
    st.header("🎨AI 로고 제작 작가에게 의뢰합니다!")

    # 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일을 업로드하면 LOGO를 생성해줘요.", type="pdf")

    def clean_text(text):
        # \n을 공백으로 대체
        text = text.replace("\n", " ")
        # 불필요한 중복 공백 제거
        text = " ".join(text.split())
        return text

    # PDF 파일 읽기
    if uploaded_file is not None:
        logo_maker = "다음 이어지는 내용을 기반으로 NGO 단체의 로고를 글자없이 독창적으로 그려줘. 그림에는 글자가 들어가면 절대 안돼."
        if uploaded_file is not None:
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        # 페이지에서 테이블 추출
                        imsi = page.extract_text()
                        logo_maker = logo_maker + imsi
            except Exception as e:
                st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {e}")

            st.session_state["pdf_file_content"] = logo_maker  # 파일 내용을 세션에 저장

    if st.session_state["pdf_file_content"] is not None:
        if st.button("로고 생성하기", key="generate_logo_button"):
            st.session_state["image_url"] = generate_logo(st.session_state["pdf_file_content"])

        # 이전에 생성된 이미지 표시
        if st.session_state["image_url"]:
            st.image(st.session_state["image_url"], caption="AI가 추천해주는 LOGO", use_container_width=True)
            st.write("LOGO Image 저장중...")
            image_response = requests.get(st.session_state["image_url"])  # 이미지 URL에서 이미지 다운로드
            image = Image.open(io.BytesIO(image_response.content))
            image_save_path = os.path.join(user_folder, "PDF_LOGO.png")
            image.save(image_save_path)

            st.success(f"Image saved at: {image_save_path}")
    st.write('---')
    # 마크다운 링크
    st.subheader("🤓 마음에 드는 로고를 골랐나요?")
    tmp = '''
        그러면 이제 로고를 최종 편집하고 포스터를 만들 차례입니다!\n
        해당 NGO 단체 이름을 눌러 로고&광고포스터를 제작하러 가봅시다.\n
        '''
    st.write(tmp)
    st.write('')
    st.write('')
    col1, col2 = st.columns(2)
    with col1:
        st.link_button(":one: **RNC**(Refugee Never Cry)" , "https://www.canva.com/design/DAGZkDtX3Es/uy5-S0e3Uknys9ZfK8SP8Q/edit"   )
    with col2:
        st.link_button(":two: **BLUE ROSE**" , "https://www.canva.com/design/DAGZkMj5gWs/0b_Kym_ArJHfOwpKGs9Z-A/edit")
    col3, col4 = st.columns(2)

    with col3:
        st.link_button(":three: **Happy Kids**" , "https://www.canva.com/design/DAGZkIJ7gvU/pxXpMKGGHeQWgEChou8cug/edit")
    with col4:
        st.link_button(":four: **C.F.W**(Children Free From Work)**" , "https://www.canva.com/design/DAGZkIOn7Us/L4Ivb2fqNNH6iUoszvRdCQ/edit")    

# Tab 3: 뉴스기사 첨삭
with tab3:
    st.header("📝AI 뉴스 편집자에게 첨삭을 요청합니다!")
    tmp2 = '''
        각 NGO 이름을 클릭해 뉴스 기사 작성본을 확인하세요.\n
        작성한 뉴스기사 파일을 편집자에게 제출해 주세요.\n
        신랄한 평가가 기다리고 있답니다.😉\n
        '''
    st.write(tmp2)
    st.write('')
    st.write('')
    col1, col2 = st.columns(2)
    with col1:
        st.link_button(":one: **RNC**(Refugee Never Cry)" , "https://docs.google.com/document/d/1RF2hzBhv26sWiacT1VQIr8HSZFB7ACzkjSiXzOuvNWs/edit?tab=t.0"   )
    with col2:
        st.link_button(":two: **BLUE ROSE**" , "https://docs.google.com/document/d/1nDKGDu5W5VKaNObZrzUvZf6amezrYngViUIOJLWsd2I/edit?tab=t.0")
    col3, col4 = st.columns(2)

    with col3:
        st.link_button(":three: **Happy Kids**" , "https://docs.google.com/document/d/1q92e22DYV1yNdMnO0paWcvAKMcWfp5_fyAPm3kv-FbE/edit?tab=t.0")
    with col4:
        st.link_button(":four: **C.F.W**(Children Free From Work)**" , "https://docs.google.com/document/d/10WBYdKRjv9xRNodh3q7Nl_O3FyhB_lCAOtGBF5_Zc10/edit?tab=t.0") 

    st.write('')
    st.write('')

    system_roles = [
        {
            "role": "system",
            "content": "너는 기사를 아주 잘 쓰는 기자야. 주어진 기사를 잘 첨삭해서 고칠 부분을 알려줘. 너무 어려운 단어는 지양부탁해.",
        }
    ]
    current_chat = system_roles
    def generate_response(messages):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # GPT 모델
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}")
            return "오류가 발생했습니다. 다시 시도해주세요."    
        
    # 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일을 업로드하면 기사를 첨삭해줘요.", type="pdf")

    def clean_text(text):
        # \n을 공백으로 대체
        text = text.replace("\n", " ")
        # 불필요한 중복 공백 제거
        text = " ".join(text.split())
        return text

    # PDF 파일 읽기
    query = "아래에 주어진 내용들 중에 고칠 부분들을 종류별로 알려줘. 맞춤법/문맥/자연스러움 정도로 나눠서 알려줘."
    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    # 페이지에서 테이블 추출
                    imsi = page.extract_text()
                    query = query + imsi
        except Exception as e:
            st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {e}")

        current_chat.append({"role": "user", "content": query})

        with st.spinner(f"AI 편집자가 고심 중 입니다..."):
            response = generate_response(current_chat)
        current_chat.append({"role": "assistant", "content": response})
        st.write(response)
