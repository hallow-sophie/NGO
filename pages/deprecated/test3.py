import streamlit as st

# 세션 상태 초기화
if "inputs" not in st.session_state:
    st.session_state["inputs"] = {"a": "", "b": "", "c": ""}  # 초기값

if "result" not in st.session_state:
    st.session_state["result"] = None

# 수식과 입력 필드 배치
st.title("수식 문제 - 입력 구멍 만들기")
st.write("아래 수식에서 빈칸에 값을 입력하세요:")

# 수식과 입력 필드
cols = st.columns([2, 2, 2, 2, 2])  # 각 열의 비율 조정
with cols[0]:
    st.write("")
    st.session_state["inputs"]["a"] = st.text_input("100", value=st.session_state["inputs"]["a"], label_visibility="collapsed")

with cols[1]:
    st.write("")
    st.write("x")

with cols[2]:
    st.session_state["inputs"]["b"] = st.text_input("분자 입력", value=st.session_state["inputs"]["b"], label_visibility="collapsed")
    st.write("---------------")
    st.session_state["inputs"]["c"] = st.text_input("분모 입력", value=st.session_state["inputs"]["c"], label_visibility="collapsed")
# with cols[1]:
#     st.session_state["inputs"]["a"] = st.text_input("분자 입력", value=st.session_state["inputs"]["a"], label_visibility="collapsed")
with cols[2]:
    st.write("")  # 나눗셈 기호

# 계산 버튼
if st.button("제출"):
    try:
        # 사용자 입력값 가져오기
        a = float(st.session_state["inputs"]["a"])
        b = float(st.session_state["inputs"]["b"])

        if b == 0:
            st.error("분모(b)는 0이 될 수 없습니다.")
        else:
            # 정답 계산
            correct_result = 100 * (a / b)
            st.session_state["result"] = correct_result
            st.success(f"정답: {correct_result:.2f}")
    except ValueError:
        st.error("모든 값은 숫자로 입력해야 합니다.")

# 결과 표시
if st.session_state["result"] is not None:
    st.write(f"계산된 값: **{st.session_state['result']:.2f}**")
