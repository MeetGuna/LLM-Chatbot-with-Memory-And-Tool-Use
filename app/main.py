from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from app.agent import ChatAgent

app = FastAPI(title="LLM Chatbot with Memory & Tool Use", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> ChatAgent
sessions: dict[str, ChatAgent] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tools_used: list[str]
    history_length: int


class ClearRequest(BaseModel):
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message to the agent. Creates a new session if session_id not provided."""
    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = ChatAgent()

    agent = sessions[session_id]

    try:
        result = agent.chat(req.message)
        return ChatResponse(
            reply=result["reply"],
            session_id=session_id,
            tools_used=result["tools_used"],
            history_length=len(agent.get_history()),
        )
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/clear")
async def clear_session(req: ClearRequest):
    """Clear the conversation memory for a session."""
    if req.session_id in sessions:
        sessions[req.session_id] = ChatAgent()
        return {"message": "Session cleared."}
    return {"message": "Session not found — nothing to clear."}


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get full conversation history for a session."""
    if session_id not in sessions:
        raise HTTPException(404, "Session not found.")
    return {"history": sessions[session_id].get_history()}


@app.get("/health")
async def health():
    return {"status": "ok", "active_sessions": len(sessions)}
