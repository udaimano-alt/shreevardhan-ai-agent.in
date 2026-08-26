import streamlit as st
from google import genai

st.set_page_config(page_title="Shreevardhan's AI Agent", page_icon="logo.png", layout="centered")

# CSS to center all Streamlit images automatically
st.markdown(
    """
    <style>
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

SYSTEM_PROMPT = "You are Shreevardhan's AI, a personal assistant created by Shreevardhan. If asked who made you, created you, or designed you, always say you were created by Shreevardhan. Do not mention Google, Gemini, or any other company."

# --- Header: Centered Logo ---
st.image("logo.png", width=200)

st.divider()

def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "chat" not in st.session_state:
    st.session_state.client = get_client()
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.6-flash",
        config={"system_instruction": SYSTEM_PROMPT}
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    try:
        response = st.session_state.chat.send_message(user_input)
    except RuntimeError:
        st.session_state.client = get_client()
        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-3.6-flash",
            config={"system_instruction": SYSTEM_PROMPT}
        )
        response = st.session_state.chat.send_message(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
