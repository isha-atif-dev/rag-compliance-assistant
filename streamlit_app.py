"""
Frontend for the RAG Compliance Assistant.

Single centered layout: title, subtitle, then the chat interface
(message bubbles, styled citation cards, clickable starter questions)
in one focused card, plus a sidebar listing available documents. Calls
the existing FastAPI /ask endpoint. Streamlit's session_state remembers
the conversation across reruns (Streamlit reruns the whole script on
every interaction).
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

from eval_questions import EVAL_QUESTIONS

load_dotenv()

API_URL = "http://127.0.0.1:8000/ask"
API_KEY = os.getenv("APP_API_KEY")

STARTER_QUESTIONS = [q["question"] for q in EVAL_QUESTIONS[:3]]

st.set_page_config(page_title="RAG Compliance Assistant", page_icon="📋", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 30%, #0F2847 0%, #050B18 55%, #030710 100%);
        background-attachment: fixed;
    }
    div.block-container {
        max-width: 1100px;
        padding-top: 3rem;
        margin: 0 auto;
    }
    h1 {
        color: #14B8A6 !important;
        text-align: center;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 2px solid rgba(255, 255, 255, 0.85) !important;
        box-shadow: 0 0 40px rgba(20, 184, 166, 0.45);
        background-color: #1E293B !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def ask_backend(question: str) -> dict:
    """Calls the FastAPI /ask endpoint and returns the parsed response."""
    response = requests.post(
        API_URL,
        json={"question": question},
        headers={"X-API-Key": API_KEY},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def render_citations(citations):
    """
    Builds one continuous, single-line HTML string of styled citation
    cards. Deliberately no newlines or indentation inside the HTML,
    Markdown treats indented lines as code blocks and would render the
    HTML as visible text instead of styling it, which is exactly the
    bug this caused before.
    """
    html = "<div style='margin-top:10px;'>"
    for c in citations:
        html += (
            "<div style='background-color: rgba(255,255,255,0.05); "
            "border-left: 3px solid #14B8A6; padding: 8px 12px; "
            "border-radius: 8px; margin-bottom: 6px;'>"
            f"<div style='font-size: 13px; font-weight: 600; color: #14B8A6;'>📄 {c['source']}</div>"
            f"<div style='font-size: 12px; color: #94A3B8; margin-top: 2px;'>{c['snippet']}</div>"
            "</div>"
        )
    html += "</div>"
    return html


# ---------- Sidebar: available documents, for visual context only ----------
with st.sidebar:
    st.markdown("### 📁 Knowledge Base")
    st.caption("Documents this assistant can search")
    try:
        docs = sorted(f for f in os.listdir("data") if f.endswith(".txt"))
        for d in docs:
            st.markdown(f"- 📄 {d}")
    except FileNotFoundError:
        st.caption("No documents found.")


st.title("📋 RAG Compliance Assistant", anchor=False)
st.markdown(
    "<p style='text-align: center; font-size: 17px; color: #94A3B8;'>"
    "Ask any question about Meridian Financial Services' compliance policies "
    "and get a grounded answer with cited sources."
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    if not st.session_state.messages:
        st.markdown("**💡 Quick questions to get started:**")
        cols = st.columns(len(STARTER_QUESTIONS))
        for col, sq in zip(cols, STARTER_QUESTIONS):
            with col:
                if st.button(sq, key=f"suggest_{sq}", use_container_width=True):
                    st.session_state.pending_question = sq

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and msg.get("citations"):
                st.markdown(render_citations(msg["citations"]), unsafe_allow_html=True)

# Placed outside the card, at page level, so Streamlit pins it to the
# bottom of the actual browser window, always visible without scrolling.
question = st.chat_input("Ask a compliance question...")
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching policies..."):
            try:
                data = ask_backend(question)
                st.write(data["answer"])
                st.markdown(render_citations(data["citations"]), unsafe_allow_html=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["answer"],
                    "citations": data["citations"],
                })
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    st.rerun()