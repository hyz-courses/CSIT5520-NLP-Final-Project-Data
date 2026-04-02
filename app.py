import streamlit as st
import requests
import json

st.set_page_config(page_title="HKUST Life Chatbot", layout="centered")

st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("HKUST Life Chatbot")

# Chat history
if "messages" not in st.session_state:  # init
    st.session_state.messages = []

for msg in st.session_state.messages:   # show
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Bar
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 回答区域
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_answer = ""

        try:
            response = requests.post(
                "https://api.docsearch.love/chat",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                json={
                    "query": prompt,
                    "user": "test-user",
                    "conversation_id": None,
                    "inputs": {}
                },
                stream=True,
                timeout=240
            )

            # SSE
            for line in response.iter_lines():
                if not line:
                    continue

                line = line.decode("utf-8").strip()
                if not line.startswith("data: "):
                    continue

                json_str = line[6:]     # "data: "

                if json_str == "[DONE]":
                    break

                try:
                    data = json.loads(json_str)
                except:
                    continue

                # Only handle "message" event
                if data.get("event") == "message":
                    answer_chunk = data.get("answer", "")
                    full_answer += answer_chunk
                    # Cursor
                    placeholder.markdown(full_answer + "▌")

            # Remove cursor after SSE done
            placeholder.markdown(full_answer)

        except Exception as e:
            full_answer = f"Error: {str(e)}"
            placeholder.markdown(full_answer)

        # Save
        st.session_state.messages.append({"role": "assistant", "content": full_answer})