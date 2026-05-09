# 🤖 LLM Chatbot with Memory & Tool Use

A production-grade conversational AI agent built with LangChain that remembers your full conversation and can use real tools — web search, calculator, Wikipedia, and live date/time.

Built as part of my AI Engineering portfolio (Feb–Mar 2025).

---

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI (session manager)
                           ↓
                    LangChain Agent (GPT-3.5)
                     ↙    ↙    ↙    ↙
              Calc  Web  Wiki  DateTime
                           ↓
              ConversationBufferWindowMemory (last 20 turns)
```

---

## ✨ Features

- **Persistent memory** — remembers the full conversation per session (last 20 turns)
- **Tool use** — agent decides which tool to use based on the question
- **4 built-in tools** — calculator, web search (DuckDuckGo, free), Wikipedia, datetime
- **Multi-session** — each browser session gets its own memory via UUID
- **Tool transparency** — UI shows which tools were used for each response
- **Quick suggestions** — clickable starter questions on empty chat

---

## 🛠️ Tools

| Tool | Trigger | Source |
|------|---------|--------|
| 🧮 Calculator | Any maths, percentages, powers | Python `math` module |
| 🌐 Web Search | News, prices, weather, recent events | DuckDuckGo (no API key needed) |
| 📖 Wikipedia | Definitions, people, history, concepts | Wikipedia API |
| 🕐 Date & Time | Current date, time, day of week | Python `datetime` + `pytz` |

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | OpenAI GPT-3.5-turbo |
| Agent framework | LangChain `create_openai_tools_agent` |
| Memory | `ConversationBufferWindowMemory` (k=20) |
| Backend | FastAPI + session management |
| Frontend | Streamlit with chat bubbles |
| Web Search | DuckDuckGo Search (free, no API key) |

---

## ⚙️ Setup

```bash
git clone https://github.com/yourusername/llm-chatbot-agent.git
cd llm-chatbot-agent

pip install -r requirements.txt

cp .env.example .env
# Add OPENAI_API_KEY to .env

# Terminal 1 — API
uvicorn app.main:app --reload --port 8000

# Terminal 2 — UI
streamlit run streamlit_app.py
```

Open http://localhost:8501

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send a message (auto-creates session) |
| POST | `/clear` | Clear memory for a session |
| GET | `/history/{session_id}` | Get full conversation history |
| GET | `/health` | Health check |

### Example

```json
POST /chat
{ "message": "What is 18% of 56000?", "session_id": null }

Response:
{
  "reply": "18% of 56,000 is 10,080.",
  "session_id": "abc-123-...",
  "tools_used": ["calculator_tool"],
  "history_length": 2
}
```

---

## 💡 Key Concepts Demonstrated

- **LangChain Agents** — `create_openai_tools_agent` with tool routing
- **Conversation memory** — `ConversationBufferWindowMemory` across turns
- **Tool design** — custom `@tool` decorated functions with clear docstrings
- **Agent reasoning** — model reads tool docstrings to decide which to call
- **Session management** — FastAPI stores per-user agent instances via UUID
- **Streaming-ready architecture** — easy to add SSE streaming

---

## 📁 Project Structure

```
llm-chatbot-agent/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI routes + session store
│   └── agent.py       # LangChain agent with memory
├── tools/
│   ├── __init__.py
│   ├── calculator.py  # Safe math evaluator
│   ├── web_search.py  # DuckDuckGo search
│   ├── datetime_tool.py # Current date/time (IST)
│   └── wiki_tool.py   # Wikipedia summaries
├── streamlit_app.py   # Chat UI with bubbles + tool badges
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧠 What I Learned

- How LangChain agents use tool docstrings to decide which tool to invoke
- `ConversationBufferWindowMemory` keeps context without hitting token limits
- FastAPI session management for multi-user stateful apps
- Designing tool descriptions that guide the LLM correctly
- The difference between chains (fixed) and agents (dynamic reasoning)

---

## 📌 Future Improvements

- [ ] Streaming responses with Server-Sent Events
- [ ] Add a code execution tool (Python REPL)
- [ ] Persistent memory across browser sessions (Redis/SQLite)
- [ ] Voice input/output
- [ ] Multi-agent: route complex queries to specialised sub-agents

---

## 👤 Author

Built by [Your Name] · [LinkedIn](https://linkedin.com/in/yourprofile) · [GitHub](https://github.com/yourusername)

> Built Feb–Mar 2025 as part of an intensive AI Engineering self-study period (Oct 2024–present).
