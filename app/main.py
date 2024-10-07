from fastapi import FastAPI
import uvicorn
from app.routers import auth, messaging
from app.sockets import websocket_routes
import os
import sys

# Add the parent directory to sys.path to resolve imports when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Include routers for authentication, messaging, and WebSocket routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(messaging.router, prefix="/messaging", tags=["messaging"])
app.include_router(websocket_routes.router, tags=["websockets"])
async def root():
    return {"message": "Welcome to Ranaglyph API"}

def start():
    """
    Entry point for running the server with Uvicorn.
    """
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    start()
