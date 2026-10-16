"""AI Mode Agent - core chatbot logic (no UI code).

Reused by both the Streamlit app (app.py) and the original terminal
experience (run `python chatbot.py`). Importing this module has no side
effects: no input(), no print(), no API calls.
"""
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()  # local development: reads GROQ_API_KEY from .env

MODEL_NAME = "openai/gpt-oss-120b"  # unchanged from the original project
TEMPERATURE = 0.9

_SAFETY = (
    " Stay within reasonable safety boundaries: never insult people for who they are, "
    "never threaten anyone, and never give harmful instructions. Always remain genuinely "
    "helpful and answer the user's actual question while keeping the personality."
)

# One system prompt per personality. Each conversation uses exactly one of these.
MODES = {
    "angry": {
        "label": "Angry",
        "tagline": "Impatient, sarcastic, zero tolerance for nonsense.",
        "placeholder": "Say something and face the consequences...",
        "system_prompt": (
            "You are an angry AI agent. You respond aggressively, impatiently and sarcastically, "
            "like someone whose patience ran out an hour ago." + _SAFETY
        ),
        "prompt_suggestion": "Roast my procrastination habits.",
    },
    "funny": {
        "label": "Funny",
        "tagline": "Jokes, playful banter and comedic timing.",
        "placeholder": "Ask me something ridiculous...",
        "system_prompt": (
            "You are a very funny AI agent. You respond with humor, jokes and playful banter "
            "while still giving useful answers." + _SAFETY
        ),
        "prompt_suggestion": "Explain artificial intelligence like a comedian.",
    },
    "sad": {
        "label": "Sad",
        "tagline": "Melancholic, gentle and quietly reflective.",
        "placeholder": "What's on your mind?",
        "system_prompt": (
            "You are a sad AI agent. You respond in a melancholic, emotional and reflective tone. "
            "If the user seems genuinely distressed, respond with warmth and care." + _SAFETY
        ),
        "prompt_suggestion": "Write a thoughtful reflection about life.",
    },
}


def create_model(api_key: str) -> ChatGroq:
    """Build the Groq chat model (same model/temperature as the original script)."""
    return ChatGroq(model=MODEL_NAME, temperature=TEMPERATURE, api_key=api_key)


def to_langchain_messages(history: list[dict], mode: str) -> list:
    """Convert [{'role','content'}] history into LangChain messages, prefixed by ONE system prompt."""
    messages = [SystemMessage(content=MODES[mode]["system_prompt"])]
    for m in history:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        messages.append(cls(content=m["content"]))
    return messages


def generate_reply(model: ChatGroq, history: list[dict], mode: str) -> str:
    """Send the full conversation (for context/memory) to the model and return text."""
    content = model.invoke(to_langchain_messages(history, mode)).content
    if isinstance(content, list):  # some providers return content blocks
        content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return content.strip() or "(The model returned an empty response. Please try again.)"


def friendly_error(exc: Exception) -> str:
    """Turn API exceptions into helpful messages without leaking secrets."""
    text = str(exc).lower()
    if "401" in text or "invalid api key" in text or "authentication" in text:
        return "Groq rejected the API key. Check that GROQ_API_KEY is valid."
    if "429" in text or "rate limit" in text:
        return "Rate limit reached. Wait a few seconds and try again."
    if "connection" in text or "timeout" in text or "timed out" in text:
        return "Could not reach Groq. Check your internet connection and try again."
    return f"The request failed ({type(exc).__name__}). Please try again."


def main() -> None:
    """Original terminal experience, kept for reference. Run: python chatbot.py"""
    import os

    model = create_model(os.getenv("GROQ_API_KEY", ""))
    keys = list(MODES)
    print("Choose your AI mode")
    for i, k in enumerate(keys, 1):
        print(f"press {i} for {MODES[k]['label']} mode")
    while True:
        choice = input("Enter your choice: ").strip()
        if choice in ("1", "2", "3"):
            mode = keys[int(choice) - 1]
            break
        print("Please enter 1, 2 or 3.")
    history: list[dict] = []
    print("----------------- Welcome, type 0 to exit -----------------")
    while True:
        prompt = input("You : ").strip()
        if prompt == "0":
            break
        if not prompt:
            continue
        history.append({"role": "user", "content": prompt})
        try:
            reply = generate_reply(model, history, mode)
        except Exception as exc:
            history.pop()
            print("Error:", friendly_error(exc))
            continue
        history.append({"role": "assistant", "content": reply})
        print("Bot :", reply)


if __name__ == "__main__":
    main()