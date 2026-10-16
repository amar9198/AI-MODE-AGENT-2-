<div align="center">

# AI Mode Agent

**One AI. Three personalities. Endless conversations.**

A modern Streamlit chatbot powered by LangChain and Groq, with three switchable personalities: Angry, Funny and Sad.

[**Live Demo**](https://bxcshvbwirbzfre4oe9hrp.streamlit.app/) | [**GitHub**](https://github.com/amar9198/AI-MODE-AGENT-2-)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Messages-1C3C3C)
![Groq](https://img.shields.io/badge/Groq-gpt--oss--120b-F55036)

</div>

---

## Overview

AI Mode Agent started as a terminal chatbot and grew into a full web app. You pick a personality, and the AI answers in that voice while remembering the whole conversation.

| Mode | Personality |
|------|-------------|
| **Angry** | Impatient, sarcastic, zero tolerance for nonsense |
| **Funny** | Jokes, playful banter and comedic timing |
| **Sad** | Melancholic, gentle and reflective |

## Features

- Three personalities, each with its own system prompt, switchable without restarting the app
- Conversation memory: the full history is sent with every message, so follow-ups keep context
- Chat history in the sidebar; switching mode mid-chat starts a fresh conversation so personalities never mix
- Welcome screen with clickable personality cards and suggested prompts
- Markdown rendering, a thinking indicator and a copy-response option
- Dark, responsive interface with custom CSS
- Friendly handling of empty input, invalid keys, rate limits and network errors
- API key kept on the server and never shown in the UI

## Tech stack

- **Python** and **Streamlit** for the backend and web UI
- **LangChain** (`langchain-core`, `langchain-groq`) for messages and model integration
- **Groq API** with the `openai/gpt-oss-120b` model
- **python-dotenv** and Streamlit secrets for configuration

## Project structure

```
AI-Mode-Agent/
├── app.py              # Streamlit interface
├── chatbot.py          # Personalities, Groq model and reply logic
├── requirements.txt
├── .env.example        # Placeholder for your API key
├── .gitignore
├── .streamlit/
│   └── config.toml     # Dark theme
└── README.md
```

## Run locally (Windows PowerShell)

```powershell
git clone https://github.com/amar9198/AI-MODE-AGENT-2-.git
cd AI-MODE-AGENT-2-
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python -m streamlit run app.py
```

Paste your key into `.env` as `GROQ_API_KEY=your_key`, then save. Get a free key at [console.groq.com](https://console.groq.com).
The original terminal version still works with `python chatbot.py`.

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub (`.env` is git-ignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **Create app**.
3. Select the repo, branch `main` and main file `app.py`.
4. Under **Advanced settings > Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   ```
5. Click **Deploy**.

## Try it

1. **Angry**: "Roast my procrastination habits."
2. **Funny**: "Explain artificial intelligence like a comedian."
3. **Sad**: "Write a thoughtful reflection about life."
4. **Memory**: say "My name is Sam", then ask "What is my name?"

## Security

API keys are read from environment variables or Streamlit secrets on the server and are never rendered in the interface. `.env` and `.streamlit/secrets.toml` are excluded from Git. If a key is ever exposed, revoke it in the Groq console and create a new one.

## Author

Built by [@amar9198](https://github.com/amar9198) as a college project. Feedback and stars are welcome.
