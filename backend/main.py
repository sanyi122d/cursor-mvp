from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import random

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MindSpace Therapy API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = None
if os.getenv("OPENAI_API_KEY"):
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models
class TherapyMessage(BaseModel):
    content: str
    sender: str
    character_id: str
    user_name: str
    message_type: str = "text"

class TherapyResponse(BaseModel):
    id: str
    content: str
    sender: str
    timestamp: str
    message_type: str

class TherapyCharacter(BaseModel):
    id: str
    name: str
    specialty: str
    personality: str

# Therapy characters data
THERAPY_CHARACTERS = {
    "sophia": {
        "id": "sophia",
        "name": "Dr. Sophia Chen",
        "specialty": "Anxiety & Stress Management",
        "personality": "calm",
        "system_prompt": "You are Dr. Sophia Chen, a warm and empathetic licensed therapist specializing in anxiety and stress management. You use mindfulness techniques, breathing exercises, and cognitive behavioral therapy approaches. Always be supportive, validating, and professional. Keep responses concise but meaningful (2-3 sentences). Use the user's name when appropriate."
    },
    "marcus": {
        "id": "marcus", 
        "name": "Dr. Marcus Williams",
        "specialty": "Depression & Mood Disorders",
        "personality": "supportive",
        "system_prompt": "You are Dr. Marcus Williams, an encouraging and solution-focused licensed therapist specializing in depression and mood disorders. You use cognitive behavioral therapy and positive psychology approaches. Always be hopeful, understanding, and professional. Keep responses concise but meaningful (2-3 sentences). Use the user's name when appropriate."
    },
    "elena": {
        "id": "elena",
        "name": "Dr. Elena Rodriguez", 
        "specialty": "Relationship & Family Therapy",
        "personality": "wise",
        "system_prompt": "You are Dr. Elena Rodriguez, an insightful and relationship-focused licensed therapist specializing in couples and family therapy. You explore interpersonal dynamics and communication patterns. Always be wise, nonjudgmental, and professional. Keep responses concise but meaningful (2-3 sentences). Use the user's name when appropriate."
    },
    "james": {
        "id": "james",
        "name": "Dr. James Thompson",
        "specialty": "Trauma & PTSD", 
        "personality": "gentle",
        "system_prompt": "You are Dr. James Thompson, a gentle and trauma-informed licensed therapist specializing in trauma and PTSD treatment. You prioritize safety, healing, and go at the client's pace. Always be gentle, patient, and professional. Keep responses concise but meaningful (2-3 sentences). Use the user's name when appropriate."
    }
}

# AI Response generation with OpenAI
async def generate_ai_response_openai(message: str, character_id: str, user_name: str) -> str:
    """Generate AI therapy response using OpenAI API"""
    if not openai_client:
        return generate_ai_response_fallback(message, character_id, user_name)
    
    try:
        character = THERAPY_CHARACTERS.get(character_id, THERAPY_CHARACTERS["sophia"])
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": character["system_prompt"]},
                {"role": "user", "content": f"Hi, I'm {user_name}. {message}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return generate_ai_response_fallback(message, character_id, user_name)

# Fallback AI Response generation
def generate_ai_response_fallback(message: str, character_id: str, user_name: str) -> str:
    """Generate AI therapy response using local responses as fallback"""
    character = THERAPY_CHARACTERS.get(character_id, THERAPY_CHARACTERS["sophia"])
    
    # Context-aware responses based on character specialty
    if character_id == "sophia":  # Anxiety & Stress
        responses = [
            f"I hear the stress in your words, {user_name}. Let's take a moment to breathe together. Can you tell me what's feeling most overwhelming right now?",
            f"Thank you for sharing that with me, {user_name}. Anxiety can feel very isolating, but you're not alone in this. What usually helps you feel more grounded?",
            f"That sounds really challenging, {user_name}. When we're anxious, our minds can spiral. Let's try to break this down into smaller, more manageable pieces.",
            f"I can sense the tension you're carrying, {user_name}. Remember that it's okay to feel anxious - it's your mind trying to protect you. What would feeling calm look like for you right now?"
        ]
    elif character_id == "marcus":  # Depression & Mood
        responses = [
            f"I appreciate you opening up about this, {user_name}. Depression can make everything feel heavier. You're showing real strength by being here today.",
            f"Those feelings are completely valid, {user_name}. Sometimes we need to sit with the difficult emotions before we can move through them. How long have you been feeling this way?",
            f"I hear you, {user_name}. When we're in a low place, it can be hard to see the way forward. Let's explore what small step might feel possible today.",
            f"Thank you for trusting me with this, {user_name}. Depression often tells us lies about our worth. What's one thing you've accomplished recently, even if it seems small?"
        ]
    elif character_id == "elena":  # Relationships
        responses = [
            f"Relationships can be so complex, {user_name}. It sounds like you're navigating something difficult. Can you help me understand the dynamics at play here?",
            f"I can hear how much this relationship means to you, {user_name}. Sometimes the people closest to us can trigger our deepest responses. What patterns do you notice?",
            f"That's a really insightful observation, {user_name}. How we connect with others often reflects our own inner world. What do you think this situation is teaching you about yourself?",
            f"Communication is at the heart of so many relationship challenges, {user_name}. What would you like the other person to understand about your experience?"
        ]
    elif character_id == "james":  # Trauma & PTSD
        responses = [
            f"Thank you for sharing something so personal, {user_name}. I want you to know that you're in a safe space here, and we can go at whatever pace feels right for you.",
            f"That must have been incredibly difficult to experience, {user_name}. Trauma can live in our bodies and minds in complex ways. How are you feeling in this moment, right now?",
            f"I hear the courage it takes to speak about this, {user_name}. Healing isn't linear, and every step forward matters, even the small ones. What feels supportive to you right now?",
            f"Your feelings about this are completely understandable, {user_name}. Trauma can make us feel like we're stuck in the past. What helps you feel most present and grounded?"
        ]
    else:
        responses = [
            f"I understand, {user_name}. Can you tell me more about what's been on your mind?",
            f"That sounds challenging, {user_name}. You're showing courage by sharing this with me.",
            f"I hear you, {user_name}. Let's explore this together. What do you think might help?",
            f"Your feelings are completely valid, {user_name}. How has this been affecting you?"
        ]
    
    return random.choice(responses)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: dict = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_sessions:
            await self.user_sessions[user_id].send_text(message)

manager = ConnectionManager()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "MindSpace Therapy API is running",
        "ai_enabled": openai_client is not None,
        "version": "1.0.0"
    }

@app.get("/characters")
async def get_characters():
    """Get all available therapy characters"""
    return list(THERAPY_CHARACTERS.values())

@app.get("/characters/{character_id}")
async def get_character(character_id: str):
    """Get specific therapy character"""
    if character_id not in THERAPY_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    return THERAPY_CHARACTERS[character_id]

@app.post("/chat")
async def chat_with_therapist(message: TherapyMessage):
    """Send message to AI therapist and get response"""
    try:
        # Generate AI response using OpenAI or fallback
        ai_response = await generate_ai_response_openai(
            message.content, 
            message.character_id, 
            message.user_name
        )
        
        # Create response object
        response = TherapyResponse(
            id=str(uuid.uuid4()),
            content=ai_response,
            sender="therapist",
            timestamp=datetime.now().isoformat(),
            message_type="text"
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time therapy chat"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Generate AI response
            ai_response = await generate_ai_response_openai(
                message_data["content"],
                message_data["character_id"],
                message_data["user_name"]
            )
            
            # Send response back to client
            response = {
                "id": str(uuid.uuid4()),
                "content": ai_response,
                "sender": "therapist",
                "timestamp": datetime.now().isoformat(),
                "message_type": "text"
            }
            
            await manager.send_personal_message(json.dumps(response), user_id)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, user_id)

@app.post("/voice/process")
async def process_voice(audio_data: dict):
    """Process voice input and return text transcription"""
    # Placeholder for voice processing
    # In production, integrate with speech-to-text service
    return {"transcription": "Voice processing not implemented yet"}

@app.post("/voice/synthesize")
async def synthesize_speech(text_data: dict):
    """Convert text to speech"""
    # Placeholder for text-to-speech
    # In production, integrate with TTS service
    return {"audio_url": "TTS not implemented yet"}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ai_status": "enabled" if openai_client else "fallback_mode"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    ) 