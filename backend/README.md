# MindSpace Therapy Backend

A FastAPI-based backend for the MindSpace Therapy platform providing AI-powered therapy conversations.

## Features

- 🤖 AI-powered therapy responses tailored to different character personalities
- 🔌 WebSocket support for real-time conversations
- 👥 Multiple therapy character specializations
- 🎙️ Voice processing endpoints (placeholders for future implementation)
- 🏥 Health check endpoints

## Therapy Characters

- **Dr. Sophia Chen** - Anxiety & Stress Management
- **Dr. Marcus Williams** - Depression & Mood Disorders  
- **Dr. Elena Rodriguez** - Relationship & Family Therapy
- **Dr. James Thompson** - Trauma & PTSD

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

- `GET /` - Root endpoint
- `GET /characters` - Get all therapy characters
- `GET /characters/{character_id}` - Get specific character
- `POST /chat` - Send message to AI therapist
- `WebSocket /ws/{user_id}` - Real-time chat connection
- `GET /health` - Health check

## Development

For development with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
``` 