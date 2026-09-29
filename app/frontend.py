import uuid
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Customer Support Agent",
    page_icon="🤖",
    layout="wide"
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session-{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = False

with st.sidebar:
    st.title("Session Controls")
    st.write(f"**Session ID:** `{st.session_state.thread_id}`")
    
    if st.button("New Chat", type="secondary", use_container_width=True):
        st.session_state.thread_id = f"session-{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.session_state.pending_approval = False
        st.rerun()

    st.divider()
    st.markdown("###  Quick Prompts")
    quick_prompts = [
        "Where is my order ORD-1001?",
        "What is your return window policy?",
        "I want a full refund for my monitor in order ORD-1002.",
        "I am furious, your service is terrible! Call a supervisor!"
    ]
    for q in quick_prompts:
        if st.button(q, key=f"quick_{q}", use_container_width=True, disabled=st.session_state.pending_approval):
            st.session_state.messages.append({"role": "user", "content": q})
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"thread_id": st.session_state.thread_id, "message": q},
                    timeout=120
                ).json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": resp.get("response", ""),
                    "intent": resp.get("intent"),
                    "tools_used": resp.get("tools_used", []),
                    "escalated": resp.get("escalated", False),
                    "ticket_id": resp.get("ticket_id"),
                    "pending_approval": resp.get("pending_approval", False)
                })
                st.session_state.pending_approval = resp.get("pending_approval", False)
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
            st.rerun()

st.title("Intelligent Support Agent")
st.caption("AI Support powered by Azure OpenAI, LangGraph, and RAG")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
       
        if msg["role"] == "assistant":
            col1, col2, col3 = st.columns(3)
            with col1:
                if msg.get("intent"):
                    st.caption(f" **Intent:** `{msg['intent']}`")
            with col2:
                if msg.get("tools_used"):
                    st.caption(f" **Tools:** `{', '.join(msg['tools_used'])}`")
            with col3:
                if msg.get("ticket_id"):
                    st.caption(f" **Ticket:** `{msg['ticket_id']}`")
                elif msg.get("escalated"):
                    st.caption(" **Status:** Escalated")


if st.session_state.pending_approval:
    st.warning(" **Manager Approval Required:** A high-risk action (e.g., refund > $100) is awaiting manual review.")
    col_app, col_rej = st.columns(2)
    with col_app:
        if st.button(" Approve Action", type="primary", use_container_width=True):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/approve",
                    json={"thread_id": st.session_state.thread_id, "approved": True},
                    timeout=120
                ).json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": res.get("final_response", "Action approved and resumed."),
                })
                st.session_state.pending_approval = False
                st.rerun()
            except Exception as e:
                st.error(f"Approval failed: {e}")
    with col_rej:
        if st.button(" Reject Action", type="secondary", use_container_width=True):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/approve",
                    json={"thread_id": st.session_state.thread_id, "approved": False},
                    timeout=120
                ).json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": res.get("final_response", "Action rejected by supervisor."),
                })
                st.session_state.pending_approval = False
                st.rerun()
            except Exception as e:
                st.error(f"Rejection request failed: {e}")


if prompt := st.chat_input("How can I assist you with your order or policy questions?", disabled=st.session_state.pending_approval):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing request..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"thread_id": st.session_state.thread_id, "message": prompt},
                    timeout=120
                ).json()

                content = response.get("response", "No response received.")
                st.markdown(content)

                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if response.get("intent"):
                        st.caption(f" **Intent:** `{response['intent']}`")
                with col2:
                    if response.get("tools_used"):
                        st.caption(f" **Tools:** `{', '.join(response['tools_used'])}`")
                with col3:
                    if response.get("ticket_id"):
                        st.caption(f" **Ticket:** `{response['ticket_id']}`")
                    elif response.get("escalated"):
                        st.caption(" **Status:** Escalated")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": content,
                    "intent": response.get("intent"),
                    "tools_used": response.get("tools_used", []),
                    "escalated": response.get("escalated", False),
                    "ticket_id": response.get("ticket_id"),
                    "pending_approval": response.get("pending_approval", False)
                })

                st.session_state.pending_approval = response.get("pending_approval", False)
                if st.session_state.pending_approval:
                    st.rerun()

            except requests.exceptions.ConnectionError:
                err_msg = "Could not reach FastAPI server. Ensure `uvicorn app.main:app --port 8000` is running."
                st.error(err_msg)
            except Exception as e:
                st.error(f"Error: {e}")