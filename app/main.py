# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

# In-Memory Chat-Log: Liste von Nachrichten
chat_log: List[dict] = []
MAX_MESSAGES = 100  # wir behalten nur die letzten 100

class ChatMessage(BaseModel):
    username: str
    message: str

@app.get("/nullix/chat")
def get_chat(since: float = 0.0):
    """
    Wird von Roblox benutzt, um neue Nachrichten zu holen.
    Parameter 'since' = Timestamp, ab wann neu.
    """
    new_messages = [m for m in chat_log if m["time"] > since]
    return {
        "messages": new_messages,
        "server_time": time.time()
    }

@app.post("/nullix/chat")
def post_chat(msg: ChatMessage):
    """
    Neue Chat-Nachricht speichern.
    """
    text = msg.message.strip()
    user = msg.username.strip()
    if not text or not user:
        return {"ok": False}

    entry = {
        "username": user,
        "message": text,
        "time": time.time()
    }
    chat_log.append(entry)
    # Log begrenzen
    if len(chat_log) > MAX_MESSAGES:
        del chat_log[0:len(chat_log)-MAX_MESSAGES]
    return {"ok": True, "entry": entry}
