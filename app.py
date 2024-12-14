import os
import tempfile
import streamlit as st
from embedchain import App

def embedchain_bot(db_path, api_key):
    return App.from_config(
        config={
            "llm": {"provider": "openai", "config": {"api_key": api_key}},
            "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
            "embedder": {"provider": "openai", "config": {"api_key": api_key}},
        }
    )

st.title("الحج والعمرة، سؤال و جواب")
st.title("Insight Pilgrim🕋")

openai_access_token = st.secrets["api_key"]

db_path = tempfile.mkdtemp()
app = embedchain_bot(db_path, openai_access_token)

pdf_file_path = None
col1, col2 = st.columns(2) 
with col1:
    if st.button("عندي سؤال عن العمرة"):
        pdf_file_path = "omrah.pdf"
with col2:
    if st.button("عندي استفسار عن الحج"):
        pdf_file_path = "hajj.pdf"

if pdf_file_path and os.path.exists(pdf_file_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        with open(pdf_file_path, "rb") as pdf_file:
            f.write(pdf_file.read())
        f.close()
        app.add(f.name, data_type="pdf_file")
    os.remove(f.name)
    print(f"تم إضافة {os.path.basename(pdf_file_path)} إلى قاعدة المعرفة!")
elif pdf_file_path:
    st.error("لم يتم العثور على ملف PDF.")

if openai_access_token:
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        answer = app.chat(prompt)
        st.session_state.messages.append({"role": "assistant", "content": answer})  # تأكد من إضافة الدور
        st.chat_message("assistant").write(answer)