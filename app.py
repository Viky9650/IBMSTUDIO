import os
import uuid
from typing import Optional, Tuple, Any, Dict

import requests
import streamlit as st
from dotenv import load_dotenv

# ---------------------------
# Load .env
# ---------------------------
load_dotenv()

BASE_URL = "https://langflow.servicesessentials.ibm.com/api/v1/run"
API_KEY_ENV = "IBM_AGENT_STUDIO_API_KEY"

API_KEY = os.getenv(API_KEY_ENV)
WORKFLOW_ID = os.getenv("WORKFLOW_ID")


# ---------------------------
# Helpers
# ---------------------------
def safe_parse_json(resp: requests.Response) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Try to parse JSON. If it fails, return (None, raw_text).
    """
    try:
        return resp.json(), None
    except ValueError:
        return None, resp.text


def extract_text(result: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Best-effort extraction of the agent's response text from common ICA/Langflow shapes.
    Works with Python 3.9+ (no `dict | None` syntax).
    """
    if not isinstance(result, dict):
        return None

    # Common Langflow/ICA nested output
    try:
        text = result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        if isinstance(text, str) and text.strip():
            return text
    except Exception:
        pass

    # Some responses might include message-like fields
    for key in ("text", "message", "output", "result", "detail"):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            return val

    # Sometimes "operation":"login" shows up
    op = result.get("operation")
    if isinstance(op, str) and op.strip():
        return f"(ICA returned operation='{op}'. This often indicates an auth/session requirement.)"

    return None


def call_workflow(prompt: str, session_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str], requests.Response]:
    """
    Call ICA workflow. Returns (json_dict_or_none, raw_text_or_none, response_obj)
    """
    if not API_KEY:
        raise RuntimeError(
            f"Missing {API_KEY_ENV}. Put it in .env like:\n"
            f"{API_KEY_ENV}=your_api_key_here"
        )
    if not WORKFLOW_ID:
        raise RuntimeError(
            "Missing WORKFLOW_ID. Put it in .env like:\n"
            "WORKFLOW_ID=8e635116-b18e-4ffb-b56d-43086b995d76"
        )

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

    resp = requests.post(url, json=payload, headers=headers, timeout=90)
    data, raw = safe_parse_json(resp)

    # If HTTP error, raise with helpful body included
    if resp.status_code >= 400:
        ct = resp.headers.get("content-type", "")
        body = (raw or "")
        if len(body) > 2000:
            body = body[:2000] + "\n... (truncated) ..."
        raise RuntimeError(f"HTTP {resp.status_code}\nContent-Type: {ct}\nBody:\n{body}")

    return data, raw, resp


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="ICA Workflow Demo", page_icon="🤖", layout="centered")
st.title("🤖 ICA Workflow Demo")
st.caption("Streamlit front-end calling your IBM Consulting Advantage workflow")

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.subheader("Connection")
    st.write(f"Workflow: `{WORKFLOW_ID or 'NOT SET'}`")
    st.write(f"Session: `{st.session_state.session_id}`")

    if API_KEY:
        st.success("API key loaded from .env")
    else:
        st.error(f"{API_KEY_ENV} not set in .env")

    if st.button("New session (reset chat)"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("If the response Content-Type is text/html, you’re likely hitting a login/redirect page.")

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_prompt = st.chat_input("Ask your workflow…")
if user_prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Calling ICA workflow..."):
            try:
                data, raw, resp = call_workflow(user_prompt, st.session_state.session_id)

                # Debug info (helpful while wiring it up)
                with st.expander("Debug (response metadata)"):
                    st.write("Status:", resp.status_code)
                    st.write("Content-Type:", resp.headers.get("content-type", ""))
                    st.write("URL:", resp.url)

                text = extract_text(data)

                if text:
                    st.markdown(text)
                    st.session_state.messages.append({"role": "assistant", "content": text})
                else:
                    # Show JSON if it exists; otherwise show raw response
                    if isinstance(data, dict):
                        st.warning("Received JSON but couldn’t locate a text field. Showing JSON.")
                        st.json(data)
                        st.session_state.messages.append({"role": "assistant", "content": str(data)})
                    else:
                        st.warning("Response was not JSON. Showing raw body.")
                        st.code((raw or "").strip() or "(empty response body)")
                        st.session_state.messages.append({"role": "assistant", "content": (raw or "(empty)")})

            except Exception as e:
                st.error(str(e))