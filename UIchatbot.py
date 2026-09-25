import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

load_dotenv()

st.set_page_config(page_title="AI Mode Agent", page_icon="🤖", layout="centered")

# ---------------- Custom styling ----------------
st.markdown(
    """
    <style>
    .title-text {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle-text {
        text-align: center;
        color: #888;
        margin-bottom: 1.5rem;
    }
    .mode-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

MODES = {
    "😡 Angry": {
        "prompt": "You are an angry AI agent. You respond aggressively and impatiently",
        "color": "#ff4b4b",
    },
    "😂 Funny": {
        "prompt": "You are very funny AI agent. You respond with humor and jokes",
        "color": "#ffb703",
    },
    "😢 Sad": {
        "prompt": "You are a sad AI agent. You respond with sad mode and emotions",
        "color": "#5c9ead",
    },
}

st.markdown('<div class="title-text">🤖 AI Mode Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Pick a personality and start chatting</div>', unsafe_allow_html=True)

# ---------------- Mode selection ----------------
if "mode_selected" not in st.session_state:
    st.session_state.mode_selected = False

if not st.session_state.mode_selected:
    st.write("### Choose your AI mode")
    choice = st.radio("Select a mode:", list(MODES.keys()), label_visibility="collapsed")

    if st.button("Start Chat 🚀", use_container_width=True):
        st.session_state.mode_selected = True
        st.session_state.mode_name = choice
        st.session_state.model = ChatGroq(model="openai/gpt-oss-120b", temperature=0.9)
        st.session_state.messages = [SystemMessage(content=MODES[choice]["prompt"])]
        st.rerun()

else:
    mode_name = st.session_state.mode_name
    mode_color = MODES[mode_name]["color"]

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            f'<span class="mode-badge" style="background:{mode_color}22;color:{mode_color};">'
            f"Mode: {mode_name}</span>",
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("🔄 Reset"):
            st.session_state.mode_selected = False
            st.session_state.pop("messages", None)
            st.rerun()

    # Render conversation (skip system message)
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)

    prompt = st.chat_input("You:")

    if prompt:
        if prompt == "0":
            st.stop()

        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Thinking..."):
            response = st.session_state.model.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))

        with st.chat_message("assistant"):
            st.write(response.content)