import streamlit as st
import requests
import os
import base64
import io

from dotenv import load_dotenv
from PIL import Image


# ==================================
# LOAD ENVIRONMENT
# ==================================

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")


if not API_KEY:
    st.error("OPENROUTER_API_KEY not found")
    st.stop()


# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(page_title="VisionChat AI", page_icon="🧠", layout="wide")


# ==================================
# SESSION MEMORY
# ==================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==================================
# SETTINGS
# ==================================

st.sidebar.title("⚙️ VisionChat")


model = st.sidebar.selectbox("AI Model", ["google/gemini-2.5-flash"])


thought_stream = st.sidebar.checkbox("🧠 Thought Stream", value=True)


if st.sidebar.button("🗑 Clear Chat"):

    st.session_state.messages = []

    st.rerun()


# ==================================
# HEADER
# ==================================

st.title("🧠 VisionChat AI")

st.caption("Multimodal AI Assistant (Chat + Image Understanding + Thought Stream)")


# ==================================
# FUNCTIONS
# ==================================


def encode_image(image_file):

    image = Image.open(image_file)

    image = image.convert("RGB")

    buffer = io.BytesIO()

    image.save(buffer, format="JPEG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def call_openrouter(messages):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "VisionChat AI",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1024,
    }

    response = requests.post(url, headers=headers, json=data, timeout=60)

    return response.json()


# ==================================
# USER INPUT
# ==================================


col1, col2 = st.columns(2)


with col1:

    prompt = st.text_input("💬 Ask something", placeholder="Describe the image")


with col2:

    uploaded_file = st.file_uploader("🖼️ Upload Image", type=["png", "jpg", "jpeg"])


# ==================================
# RUN VISIONCHAT AI
# ==================================


if st.button("🚀 Run VisionChat"):

    if not prompt and not uploaded_file:

        st.warning("Please enter text or upload image")

        st.stop()

    # Thought Stream

    if thought_stream:

        with st.expander("🧠 Thought Stream"):

            st.write("🔍 Understanding user request...")

            st.write("👁️ Analyzing visual information...")

            st.write("🤖 Generating AI response...")

    try:

        # IMAGE + TEXT

        if uploaded_file:

            image = Image.open(uploaded_file)

            st.image(image, caption="Uploaded Image", width="stretch")

            image_base64 = encode_image(uploaded_file)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ]

        # TEXT CHAT

        else:

            messages = st.session_state.messages + [{"role": "user", "content": prompt}]

        # API CALL

        result = call_openrouter(messages)

        if "error" in result:

            st.error(result["error"]["message"])

            st.stop()

        answer = result["choices"][0]["message"]["content"]

        # STORE MEMORY

        st.session_state.messages.append({"role": "user", "content": prompt})

        st.session_state.messages.append({"role": "assistant", "content": answer})

        # RESPONSE

        st.subheader("🤖 VisionChat Response")

        st.write(answer)

    except Exception as e:

        st.error(f"Error: {e}")


# ==================================
# HISTORY
# ==================================


st.divider()


st.subheader("📜 Chat History")


for message in st.session_state.messages:

    if message["role"] == "user":

        st.write("🧑 You:", message["content"])

    else:

        st.write("🤖 VisionChat:", message["content"])
