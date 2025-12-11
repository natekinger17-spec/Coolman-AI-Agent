from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import AsyncIterator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from coolman_agent import create_coolman_agent
from agent_framework import ChatThread

app = FastAPI(title="Coolman Fuels API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active agent and sessions
agent = None
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class SessionResponse(BaseModel):
    session_id: str

@app.on_event("startup")
async def startup_event():
    global agent
    agent = await create_coolman_agent()
    print("✅ Coolman Fuels Agent initialized")

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Shutting down...")

@app.post("/session/new")
async def new_session():
    """Create a new chat session"""
    session_id = os.urandom(16).hex()
    sessions[session_id] = agent.get_new_thread()
    return {"session_id": session_id}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Send a message and get a response"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Get or create session
    if request.session_id and request.session_id in sessions:
        thread = sessions[request.session_id]
    else:
        thread = agent.get_new_thread()
        session_id = os.urandom(16).hex()
        sessions[session_id] = thread
    
    # Get response
    response_text = ""
    async for chunk in agent.run_stream(request.message, thread=thread):
        if chunk.text:
            response_text += chunk.text
    
    return {
        "response": response_text,
        "session_id": session_id if not request.session_id else request.session_id
    }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Send a message and stream the response"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Get or create session
    if request.session_id and request.session_id in sessions:
        thread = sessions[request.session_id]
    else:
        thread = agent.get_new_thread()
        session_id = os.urandom(16).hex()
        sessions[session_id] = thread
    
    async def generate():
        async for chunk in agent.run_stream(request.message, thread=thread):
            if chunk.text:
                yield chunk.text
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/")
async def root():
    return {"message": "Coolman Fuels API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_ready": agent is not None}
