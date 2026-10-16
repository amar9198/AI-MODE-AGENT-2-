"""AI Mode Agent - Streamlit web UI."""
import os
import uuid

import streamlit as st

from chatbot import MODEL_NAME, MODES, create_model, friendly_error, generate_reply

st.set_page_config(page_title="AI Mode Agent", page_icon=":material/smart_toy:", layout="wide")

# ---------------------------------------------------------------- theme / style
ACCENTS = {  # (primary, secondary, material icon)
    "angry": ("#ff5a4d", "#ff9f43", ":material/local_fire_department:"),
    "funny": ("#fcd34d", "#22d3ee", ":material/sentiment_very_satisfied:"),
    "sad": ("#7c8cf8", "#a78bfa", ":material/water_drop:"),
}
ICON_SVG = {  # inline icons for the personality cards
    "angry": '<path d="M12 2c1 4 5 5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-4-1-6 1-9z"/>',
    "funny": '<circle cx="12" cy="12" r="9"/><path d="M8 14c1 2 2.5 3 4 3s3-1 4-3M9 9.5h.01M15 9.5h.01"/>',
    "sad": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.500 6-11 6-11z"/>',
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', system-ui, sans-serif; }
.stApp { background: radial-gradient(1200px 600px at 80% -10%, #1d1a4a 0%, transparent 60%), #0b0f1a; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 980px; padding-top: 2rem; padding-bottom: 6rem; }
[data-testid="stSidebar"] { background: #0e1424; border-right: 1px solid #1f2740; }
[data-testid="stSidebar"] .stButton > button { justify-content: flex-start; }
.stButton > button { border-radius: 12px; border: 1px solid #263052; background: #121a30; color: #e6e9f5;
  transition: all .18s ease; }
.stButton > button:hover { border-color: #7c5cff; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(124,92,255,.25); }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #6d4aff, #3b82f6); border: 0; color: #fff; }
.brand { display:flex; align-items:center; gap:.6rem; font-weight:700; font-size:1.15rem; margin-bottom:.8rem; }
.brand .logo { width:34px; height:34px; border-radius:10px; display:grid; place-items:center;
  background: linear-gradient(135deg,#7c5cff,#22d3ee); color:#fff; font-size:1rem; }
.section-label { text-transform:uppercase; letter-spacing:.08em; font-size:.7rem; color:#7f89aa; margin:1rem 0 .4rem; }
.hero-title { font-size:2.1rem; font-weight:700; line-height:1.15; margin:0;
  background: linear-gradient(90deg,#fff,#b9a8ff 60%,#67e8f9); -webkit-background-clip:text; color:transparent; }
.hero-sub { color:#9aa4c7; margin:.25rem 0 .8rem; }
.pill { display:inline-flex; align-items:center; gap:.4rem; padding:.28rem .8rem; border-radius:999px;
  font-size:.8rem; font-weight:600; border:1px solid var(--a1); color:var(--a1); background:rgba(255,255,255,.03); }
.dot { width:8px; height:8px; border-radius:50%; background:var(--c); box-shadow:0 0 8px var(--c); }
.welcome h2 { font-size:2.4rem; font-weight:700; margin:1.5rem 0 .3rem; color:#f1f3ff; }
.welcome p { color:#9aa4c7; max-width:620px; }
.pcard { border-radius:18px; padding:1.1rem 1.1rem 1rem; background: linear-gradient(160deg, rgba(255,255,255,.04), rgba(255,255,255,.01));
  border:1px solid #263052; min-height:150px; transition: all .2s ease; }
.pcard:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,.35); }
.pcard.sel { border-color: var(--a1); box-shadow: 0 0 0 1px var(--a1), 0 10px 30px color-mix(in srgb, var(--a1) 25%, transparent); }
.pcard svg { width:28px; height:28px; stroke:var(--a1); fill:none; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
.pcard h4 { margin:.5rem 0 .2rem; color:#f1f3ff; } .pcard span { color:#9aa4c7; font-size:.9rem; }
[data-testid="stChatMessage"] { border-radius:16px; padding:.9rem 1rem; border:1px solid #1f2740; background:#0f1527; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:#151b36; border-color:#2a3366; }
[data-testid="stChatInput"] { border-radius:16px; }
.thinking span { display:inline-block; width:8px; height:8px; margin-right:5px; border-radius:50%; background:var(--a1);
  animation: bounce 1.2s infinite ease-in-out; } .thinking span:nth-child(2){animation-delay:.15s} .thinking span:nth-child(3){animation-delay:.3s}
@keyframes bounce { 0%,80%,100%{transform:scale(.5);opacity:.4} 40%{transform:scale(1);opacity:1} }
.footer { text-align:center; color:#6b7595; font-size:.78rem; margin-top:2.5rem; }
@media (max-width: 768px) { .hero-title{font-size:1.6rem} .welcome h2{font-size:1.7rem} .block-container{padding:1rem 1rem 6rem} }
</style>
"""

# ---------------------------------------------------------------- state helpers
def api_key() -> str:
    """Local .env / environment variable first, then Streamlit secrets (deployment)."""
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets["GROQ_API_KEY"]
        except Exception:  # no secrets file / key missing
            key = ""
    return key.strip()


@st.cache_resource(show_spinner=False)
def get_model(key: str):
    return create_model(key)  # created once, not on every rerun


def new_conversation(mode: str) -> None:
    cid = uuid.uuid4().hex[:8]
    st.session_state.conversations[cid] = {"mode": mode, "title": "New chat", "messages": []}
    st.session_state.active = cid


def active() -> dict:
    return st.session_state.conversations[st.session_state.active]


def set_mode(mode: str) -> None:
    """Explicit, predictable switching: a conversation keeps one personality for life.
    Switching mid-chat therefore starts a fresh conversation (old one stays in history)."""
    st.session_state.confirm_clear = False
    if active()["mode"] == mode:
        return
    if active()["messages"]:
        new_conversation(mode)
        st.toast(f"Switched to {MODES[mode]['label']} mode - started a new conversation.")
    else:
        active()["mode"] = mode
    st.session_state.mode = mode


def open_conversation(cid: str) -> None:
    st.session_state.active = cid
    st.session_state.mode = st.session_state.conversations[cid]["mode"]
    st.session_state.confirm_clear = False


def start_new_chat() -> None:
    new_conversation(st.session_state.mode)
    st.session_state.confirm_clear = False


def clear_conversation() -> None:
    active()["messages"] = []
    active()["title"] = "New chat"
    st.session_state.confirm_clear = False


def queue_prompt(text: str) -> None:
    st.session_state.pending = text


if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.mode = "funny"
    st.session_state.confirm_clear = False
    new_conversation("funny")

mode = active()["mode"]
a1, a2, _ = ACCENTS[mode]
key = api_key()
ready = bool(key)

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(f"<style>:root{{--a1:{a1};--a2:{a2};}}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown('<div class="brand"><div class="logo">AI</div>AI Mode Agent</div>', unsafe_allow_html=True)
    st.button("New chat", icon=":material/add:", on_click=start_new_chat, use_container_width=True, type="primary")

    st.markdown('<div class="section-label">Personality</div>', unsafe_allow_html=True)
    for k, m in MODES.items():
        st.button(m["label"], key=f"side_{k}", icon=ACCENTS[k][2], on_click=set_mode, args=(k,),
                  use_container_width=True, type="primary" if k == mode else "secondary")

    st.markdown('<div class="section-label">History</div>', unsafe_allow_html=True)
    shown = [(cid, c) for cid, c in st.session_state.conversations.items() if c["messages"]]
    if not shown:
        st.caption("Your conversations will appear here.")
    for cid, c in reversed(shown):
        st.button(c["title"], key=f"h_{cid}", icon=ACCENTS[c["mode"]][2], on_click=open_conversation,
                  args=(cid,), use_container_width=True,
                  type="primary" if cid == st.session_state.active else "secondary")

    st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)
    if st.session_state.confirm_clear:
        st.warning("Clear all messages in this conversation?")
        c1, c2 = st.columns(2)
        c1.button("Yes, clear", on_click=clear_conversation, use_container_width=True)
        c2.button("Cancel", on_click=lambda: st.session_state.update(confirm_clear=False), use_container_width=True)
    else:
        st.button("Clear conversation", icon=":material/delete:", disabled=not active()["messages"],
                  on_click=lambda: st.session_state.update(confirm_clear=True), use_container_width=True)

    with st.expander("Settings & about"):
        st.markdown(f"**Model:** `{MODEL_NAME}`  \n**Personality:** {MODES[mode]['label']}")
        st.caption("One AI with three personalities, built with Python, LangChain and Groq. "
                   "Each personality has its own system prompt, and the full conversation is sent "
                   "with every message so follow-ups keep context.")
        st.caption("Privacy: the API key stays on the server (environment variable or Streamlit secrets) "
                   "and is never shown in this interface.")

    dot = "#34d399" if ready else "#f87171"
    st.markdown(f'<div class="pill" style="--a1:{dot};--c:{dot};margin-top:.8rem"><span class="dot"></span>'
                f'{"Model connected" if ready else "API key missing"}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- header
h1, h2 = st.columns([4, 1], vertical_alignment="center")
with h1:
    st.markdown('<p class="hero-title">AI Mode Agent</p>'
                '<p class="hero-sub">One AI. Three personalities. Endless conversations.</p>'
                f'<span class="pill" style="--c:{a1}"><span class="dot"></span>{MODES[mode]["label"]} mode</span> '
                f'<span class="pill" style="--a1:{"#34d399" if ready else "#f87171"};--c:{"#34d399" if ready else "#f87171"}">'
                f'<span class="dot"></span>{"Ready to chat" if ready else "Not configured"}</span>',
                unsafe_allow_html=True)
with h2:
    st.button("New conversation", icon=":material/edit_square:", on_click=start_new_chat, use_container_width=True,
              key="hdr_new")

if not ready:
    st.error("`GROQ_API_KEY` was not found. Add it to your local `.env` file, or to Streamlit secrets "
             "when deployed (see README). The chat is disabled until then.")

# ---------------------------------------------------------------- input (always rendered so it stays pinned)
user_text = st.chat_input(MODES[mode]["placeholder"], disabled=not ready, max_chars=4000)
if not user_text and "pending" in st.session_state:
    user_text = st.session_state.pop("pending")
if user_text is not None:
    user_text = user_text.strip()
    if user_text == "0":  # legacy terminal exit command: never sent to the model
        st.info("`0` was the exit command in the terminal version. Use **New chat** or **Clear conversation** here.")
        user_text = None
    elif not user_text:
        st.warning("Please type a message first.")
        user_text = None

conv = active()

# ---------------------------------------------------------------- welcome screen
if not conv["messages"] and not user_text:
    st.markdown('<div class="welcome"><h2>Meet your AI, your way.</h2>'
                '<p>Pick a personality, then start talking. Each one answers with its own voice and remembers '
                'the conversation as it goes.</p></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (k, m) in zip(cols, MODES.items()):
        c1, c2, _ = ACCENTS[k]
        with col:
            st.markdown(f'<div class="pcard {"sel" if k == mode else ""}" style="--a1:{c1}">'
                        f'<svg viewBox="0 0 24 24">{ICON_SVG[k]}</svg><h4>{m["label"]} mode</h4>'
                        f'<span>{m["tagline"]}</span></div>', unsafe_allow_html=True)
            st.button("Selected" if k == mode else f"Activate {m['label']}", key=f"card_{k}", on_click=set_mode,
                      args=(k,), use_container_width=True, disabled=(k == mode))
    st.markdown('<div class="section-label" style="margin-top:1.5rem">Try a prompt</div>', unsafe_allow_html=True)
    for k, m in MODES.items():
        st.button(f"{m['label']}: {m['prompt_suggestion']}", key=f"sugg_{k}", icon=ACCENTS[k][2],
                  on_click=lambda k=k: (set_mode(k), queue_prompt(MODES[k]["prompt_suggestion"])),
                  disabled=not ready, use_container_width=True)

# ---------------------------------------------------------------- chat
def render(role: str, content: str) -> None:
    with st.chat_message(role, avatar=":material/person:" if role == "user" else ":material/smart_toy:"):
        st.markdown(content)
        if role == "assistant":
            with st.expander("Copy response"):
                st.code(content, language=None)  # code blocks have a built-in copy button


for m in conv["messages"]:
    render(m["role"], m["content"])

if user_text and ready:
    if not conv["messages"]:
        conv["title"] = user_text[:32] + ("..." if len(user_text) > 32 else "")
    conv["messages"].append({"role": "user", "content": user_text})
    render("user", user_text)
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        slot = st.empty()
        slot.markdown('<div class="thinking"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
        try:
            reply = generate_reply(get_model(key), conv["messages"], conv["mode"])
        except Exception as exc:
            conv["messages"].pop()  # keep history clean so the user can resend
            slot.empty()
            st.error(f"{friendly_error(exc)} Your message was not sent, please try again.")
        else:
            slot.empty()
            conv["messages"].append({"role": "assistant", "content": reply})
            st.rerun()  # redraw so the sidebar history and copy buttons update

st.markdown('<div class="footer">AI Mode Agent | Built with Python, LangChain &amp; Groq.</div>', unsafe_allow_html=True)