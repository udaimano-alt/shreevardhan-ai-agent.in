<html>
<head>
<title>https://shreevardhan-ai-agentin-ajka7il36xov6qkg9sqezc.streamlit.app/ homepage</title>
<meta name="google-site-verification" content="<meta name="google-site-verification" content="<meta name="google-site-verification" content="a32XDgdg63yfiCx5YuMq-yZ3k3206cLSO9f9zu8iYbE" /> 
</head>
</body>
import base64
import json
import os
import uuid
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Shreevardhan's AI Agent", page_icon="logo.png", layout="centered")

HISTORY_FILE = "chat_history.json"

# Helper functions to persist chat history locally
def load_all_chats():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_all_chats(chats):
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f, indent=4)

# Header Logo Renderer
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

def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Load persistent chats from file storage
chats_db = load_all_chats()

# Initialize or restore active chat session ID
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in chats_db:
    if chats_db:
        st.session_state.current_chat_id = list(chats_db.keys())[-1]
    else:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_chat_id = new_id
        chats_db[new_id] = {"title": "New Chat", "messages": []}
        save_all_chats(chats_db)

# --- Sidebar: New Chat Button & Past Conversations ---
with st.sidebar:
    st.header("Chat Sessions")
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_chat_id = new_id
        chats_db[new_id] = {"title": "New Chat", "messages": []}
        save_all_chats(chats_db)
        st.rerun()

    st.divider()
    st.subheader("History")
    for cid in reversed(list(chats_db.keys())):
        title = chats_db[cid].get("title", "Chat")
        is_active = cid == st.session_state.current_chat_id
        label = f"👉 {title}" if is_active else f"💬 {title}"
        if st.button(label, key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# --- Main App Area ---
active_id = st.session_state.current_chat_id
current_chat = chats_db[active_id]

render_logo("logo.png", width_px=220)
st.divider()

# Format previous messages to sync with Gemini's API history context
formatted_history = []
for m in current_chat["messages"]:
    role = "user" if m["role"] == "user" else "model"
    formatted_history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

client = get_client()
gemini_chat = client.chats.create(
    model="gemini-3.6-flash",
    config={"system_instruction": SYSTEM_PROMPT},
    history=formatted_history
)

# Display active conversation messages
for msg in current_chat["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    # Append & display user input
    current_chat["messages"].append({"role": "user", "content": user_input})
    
    # Auto-rename "New Chat" title based on the first prompt
    if current_chat["title"] == "New Chat":
        current_chat["title"] = user_input[:18] + "..." if len(user_input) > 18 else user_input

    chats_db[active_id] = current_chat
    save_all_chats(chats_db)
    st.chat_message("user").write(user_input)

    # Stream assistant response
    with st.chat_message("assistant"):
        with st.spinner(""):
            response_stream = gemini_chat.send_message_stream(user_input)
            
            def generate_chunks():
                for chunk in response_stream:
                    yield chunk.text

            full_response = st.write_stream(generate_chunks())

    # Save complete assistant response to storage
    current_chat["messages"].append({"role": "assistant", "content": full_response})
    chats_db[active_id] = current_chat
    save_all_chats(chats_db)
