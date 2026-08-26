import base64
import streamlit as st
from google import genai

st.set_page_config(page_title="Shreevardhan's AI Agent", page_icon="logo.png", layout="centered")

def render_logo(image_path, width_px=220):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; padding: 10px 0;">
                <img src="data:image/png;base64,{encoded_string}" style="width: {width_px}px; max-width: 80%; height: auto; border-radius: 12px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.image(image_path, width=width_px)

SYSTEM_PROMPT = "You are Shreevardhan's AI, a personal assistant created by Shreevardhan. If asked who made you, created you, or designed you, always say you were created by Shreevardhan. Do not mention Google, Gemini, or any other company."

render_logo("logo.png", width_px=220)
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

    with st.chat_message("assistant"):
        # Shows an animated loading spinner inside the chat bubble
        with st.spinner("Thinking..."):
            def generate_chunks():
                try:
                    response = st.session_state.chat.send_message_stream(user_input)
                    for chunk in response:
                        yield chunk.text
                except Exception:
                    st.session_state.client = get_client()
                    st.session_state.chat = st.session_state.client.chats.create(
                        model="gemini-3.6-flash",
                        config={"system_instruction": SYSTEM_PROMPT}
                    )
                    response = st.session_state.chat.send_message_stream(user_input)
                    for chunk in response:
                        yield chunk.text

            full_response = st.write_stream(generate_chunks())

    st.session_state.messages.append({"role": "assistant", "content": full_response})
                
