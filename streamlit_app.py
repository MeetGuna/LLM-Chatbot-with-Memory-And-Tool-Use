import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .chat-title { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
  .chat-sub   { font-size: 0.85rem; color: #94a3b8; margin-bottom: 1.2rem; }

  /* Bubbles */
  .bubble-wrap { display:flex; margin: 6px 0; }
  .bubble-wrap.user  { justify-content: flex-end; }
  .bubble-wrap.bot   { justify-content: flex-start; }
  .bubble {
    max-width: 72%; padding: 10px 14px; border-radius: 16px;
    font-size: 0.92rem; line-height: 1.55;
  }
  .bubble.user { background:#4f46e5; color:#fff; border-bottom-right-radius:4px; }
  .bubble.bot  { background:#f1f5f9; color:#0f172a; border-bottom-left-radius:4px; }

  /* Tool badges */
  .tool-row { display:flex; gap:6px; flex-wrap:wrap; margin-top:5px; }
  .tool-badge {
    font-size:10px; font-weight:600; padding:2px 8px; border-radius:20px;
    border:1px solid;
  }
  .tool-calculator { background:#fef9c3; color:#854d0e; border-color:#fde68a; }
  .tool-web_search { background:#dbeafe; color:#1e40af; border-color:#bfdbfe; }
  .tool-get_datetime { background:#dcfce7; color:#166534; border-color:#bbf7d0; }
  .tool-wikipedia { background:#f3e8ff; color:#6b21a8; border-color:#e9d5ff; }

  /* Sidebar */
  .mem-head { font-size:11px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:.06em; margin-bottom:8px; }
  .mem-item { font-size:11px; color:#475569; padding:5px 8px; border-radius:6px; margin-bottom:4px; background:#f8fafc; border-left:3px solid #c7d2fe; }
  .mem-item.user-mem { border-left-color:#818cf8; }
  .mem-item.bot-mem  { border-left-color:#94a3b8; }

  .tool-legend { font-size:11px; color:#64748b; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []   # {"role","content","tools_used"}

# ── Layout ────────────────────────────────────────────────────────────────────
col_chat, col_side = st.columns([3, 1], gap="large")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with col_side:
    st.markdown("### 🛠️ Tools Available")
    st.markdown("""
    <div class="tool-legend">🧮 <b>Calculator</b> — maths & expressions</div>
    <div class="tool-legend">🌐 <b>Web Search</b> — live news & facts</div>
    <div class="tool-legend">🕐 <b>Date & Time</b> — current IST time</div>
    <div class="tool-legend">📖 <b>Wikipedia</b> — definitions & history</div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🧠 Memory")
    if st.session_state.messages:
        st.markdown('<div class="mem-head">Conversation so far</div>', unsafe_allow_html=True)
        # Show last 6 messages in sidebar
        recent = st.session_state.messages[-6:]
        for m in recent:
            role_class = "user-mem" if m["role"] == "user" else "bot-mem"
            icon = "👤" if m["role"] == "user" else "🤖"
            snippet = m["content"][:60] + ("..." if len(m["content"]) > 60 else "")
            st.markdown(
                f'<div class="mem-item {role_class}">{icon} {snippet}</div>',
                unsafe_allow_html=True
            )
    else:
        st.caption("No conversation yet.")

    st.divider()

    if st.button("🗑️ Clear Memory", use_container_width=True):
        if st.session_state.session_id:
            requests.post(f"{API_URL}/clear", json={"session_id": st.session_state.session_id})
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

    if st.session_state.session_id:
        st.caption(f"Session: `{st.session_state.session_id[:12]}...`")
        st.caption(f"Messages: {len(st.session_state.messages)}")

# ── CHAT PANEL ────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown('<div class="chat-title">🤖 AI Chatbot with Memory & Tool Use</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-sub">Powered by GPT-3.5 · LangChain Agents · Remembers your full conversation</div>', unsafe_allow_html=True)

    # Starter suggestions (only when empty)
    if not st.session_state.messages:
        st.markdown("**Try asking:**")
        suggestions = [
            "What is 15% of 84,500?",
            "What is the latest news about AI in India?",
            "What day is it today?",
            "Who is Sundar Pichai?",
            "What is 2 to the power of 16?",
        ]
        cols = st.columns(len(suggestions))
        for col, sug in zip(cols, suggestions):
            with col:
                if st.button(sug, use_container_width=True, key=f"sug_{sug[:10]}"):
                    st.session_state._pending_input = sug
                    st.rerun()
        st.divider()

    # Render message history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            align = "user" if msg["role"] == "user" else "bot"
            bubble_cls = "user" if msg["role"] == "user" else "bot"

            tools_html = ""
            if msg.get("tools_used"):
                badges = ""
                icons = {
                    "calculator_tool": ("🧮", "tool-calculator"),
                    "web_search_tool": ("🌐", "tool-web_search"),
                    "datetime_tool": ("🕐", "tool-get_datetime"),
                    "wiki_tool": ("📖", "tool-wikipedia"),
                }
                for t in msg["tools_used"]:
                    icon, cls = icons.get(t, ("🔧", "tool-calculator"))
                    label = t.replace("_tool", "").replace("_", " ").title()
                    badges += f'<span class="tool-badge {cls}">{icon} {label}</span>'
                tools_html = f'<div class="tool-row">{badges}</div>'

            content_escaped = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                f'<div class="bubble-wrap {align}">'
                f'<div class="bubble {bubble_cls}">{content_escaped}{tools_html}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Input area
    st.markdown("---")
    input_col, btn_col = st.columns([6, 1])
    with input_col:
        pending = getattr(st.session_state, "_pending_input", "")
        user_input = st.text_input(
            "Message",
            value=pending,
            placeholder="Ask me anything — I remember our conversation...",
            label_visibility="collapsed",
            key="chat_input"
        )
        if pending:
            del st.session_state._pending_input

    with btn_col:
        send = st.button("Send ➤", use_container_width=True, type="primary")

    if send and user_input.strip():
        # Add user message to UI immediately
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip(),
            "tools_used": []
        })

        with st.spinner("Thinking..."):
            try:
                resp = requests.post(f"{API_URL}/chat", json={
                    "message": user_input.strip(),
                    "session_id": st.session_state.session_id
                }, timeout=30)

                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["reply"],
                        "tools_used": data.get("tools_used", [])
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {resp.json().get('detail', 'Something went wrong.')}",
                        "tools_used": []
                    })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Connection error: {e}",
                    "tools_used": []
                })

        st.rerun()
