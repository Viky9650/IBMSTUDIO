import os
import uuid
from typing import Optional, Tuple, Any, Dict

import requests
import streamlit as st
from dotenv import load_dotenv

import pandas as pd
import io

# Optional document parsers
from PyPDF2 import PdfReader
import docx


# ---------------------------
# Load ENV
# ---------------------------
load_dotenv()

BASE_URL = "https://langflow.servicesessentials.ibm.com/api/v1/run"

API_KEY = os.getenv("IBM_AGENT_STUDIO_API_KEY")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")


# ---------------------------
# Helpers
# ---------------------------
def safe_parse_json(resp):

    try:
        return resp.json(), None
    except:
        return None, resp.text


def extract_text(result):

    if not isinstance(result, dict):
        return None

    try:
        return result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except:
        pass

    for k in ["text", "message", "output", "result"]:
        if k in result:
            return result[k]

    return None


def call_workflow(prompt, session_id):

    url = f"{BASE_URL}/{WORKFLOW_ID}"

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "input_value": prompt,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": session_id,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)

    data, raw = safe_parse_json(resp)

    if resp.status_code >= 400:
        raise RuntimeError(f"HTTP {resp.status_code}\n{raw}")

    return data, raw, resp


# ---------------------------
# File Parsing
# ---------------------------
def parse_file(uploaded_file):

    name = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    try:

        # Text files
        if name.endswith((".txt", ".md", ".log", ".json")):
            return file_bytes.decode("utf-8", errors="ignore")

        # CSV
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
            return df.to_string()

        # Excel
        if name.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(file_bytes))
            return df.to_string()

        # PDF
        if name.endswith(".pdf"):

            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            return text

        # Word
        if name.endswith(".docx"):

            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join(p.text for p in doc.paragraphs)

            return text

        # Images
        if uploaded_file.type.startswith("image"):
            st.image(file_bytes, caption=uploaded_file.name)
            return f"[Image uploaded: {uploaded_file.name}]"

        return f"[Unsupported file: {uploaded_file.name}]"

    except Exception as e:
        return f"[Could not parse {uploaded_file.name}: {e}]"


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="ICA Workflow Chat", page_icon="🤖")

st.title("🤖 ICA Workflow Chat + File Analysis")

# ---------------------------
# Session state
# ---------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "files_text" not in st.session_state:
    st.session_state.files_text = ""


# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:

    st.subheader("Connection")

    st.write("Workflow:", WORKFLOW_ID)
    st.write("Session:", st.session_state.session_id)

    if API_KEY:
        st.success("API key loaded")
    else:
        st.error("Missing API key")

    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.files_text = ""
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()


# ---------------------------
# File Upload
# ---------------------------
uploaded_files = st.file_uploader(
    "Upload files (images, pdf, excel, word, text)",
    accept_multiple_files=True
)

if uploaded_files:

    combined_text = ""

    for file in uploaded_files:

        st.success(f"Uploaded: {file.name}")

        parsed = parse_file(file)

        combined_text += f"\n\nFILE: {file.name}\n{parsed[:4000]}"

        with st.expander(f"Preview: {file.name}"):
            st.text(parsed[:2000])

    st.session_state.files_text = combined_text


# ---------------------------
# Chat History
# ---------------------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------------------
# Chat Input
# ---------------------------
prompt = st.chat_input("Ask about your files or workflow...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    final_prompt = prompt

    if st.session_state.files_text:

        final_prompt = f"""
User question:
{prompt}

Uploaded files content:
{st.session_state.files_text[:12000]}
"""

    with st.chat_message("assistant"):

        with st.spinner("Running workflow..."):

            try:

                data, raw, resp = call_workflow(
                    final_prompt,
                    st.session_state.session_id
                )

                text = extract_text(data)

                if text:

                    st.markdown(text)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": text}
                    )

                elif data:

                    st.json(data)

                else:

                    st.code(raw)

            except Exception as e:

                st.error(str(e))