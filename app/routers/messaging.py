from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging
from fastapi.security import OAuth2PasswordBearer
from app.services.messaging import MessagingService
from app.schemas.message import MessageCreate, MessageResponse, MessageRequest
from app.schemas.user import User
from app.services.auth import get_current_user
from app.models.user import User as UserModel
from app.db import get_db

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dependency to access the messaging service
messaging_service = MessagingService()

@router.post("/send", response_model=MessageResponse, summary="Send a message to another user")
async def send_message(
        request: MessageRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),  # Token is automatically extracted from the Authorization header
        current_user: User = Depends(get_current_user)
):
    """
    Endpoint to send a message.
    """
    logging.info(f"Current user attempting to send a message: {current_user.username}")

    # Ensure current user is available
    if not current_user:
        logging.error("Current user is None after token validation.")
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Find the recipient user based on the provided username or email
    receiver = None
    if request.receiver_username:
        receiver = db.query(UserModel).filter(UserModel.username == request.receiver_username).first()
    elif request.receiver_email:
        receiver = db.query(UserModel).filter(UserModel.email == request.receiver_email).first()

    if not receiver:
        logging.error("Receiver not found.")
        raise HTTPException(status_code=404, detail="Receiver not found.")

    logging.info(f"Receiver found: {receiver.username}")

    # Prepare the message data
    message_data = MessageCreate(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=request.content
    )

    try:
        # Send the message
        message = await messaging_service.send_message(message_data, db)
        logging.info(f"Message successfully sent from {current_user.username} to {receiver.username}.")
        return message
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/get/{user_id}", response_model=List[MessageResponse], summary="Retrieve messages with a specific user")
async def get_messages(
        user_id: int,  # Assuming user_id is an integer
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),  # Token is automatically extracted from the Authorization header
        current_user: User = Depends(get_current_user)
):
    """
    Endpoint to get messages between the current user and a specific user.
    """
    logging.info(f"Current user attempting to retrieve messages: {current_user.username}")

    if not current_user:
        logging.error("Current user is None after token validation.")
        raise HTTPException(status_code=401, detail="Unauthorized")

    if user_id == current_user.id:
        logging.error("User attempted to retrieve messages with themselves.")
        raise HTTPException(status_code=400, detail="Cannot retrieve messages with yourself.")

    logging.info(f"Retrieving messages between {current_user.username} and user ID {user_id}")

    try:
        messages = await messaging_service.get_messages(current_user.id, user_id, db)
        logging.info(f"Messages between {current_user.username} and user ID {user_id} retrieved successfully.")
        return messages
    except Exception as e:
        logging.error(f"Failed to retrieve messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")


@router.delete("/delete/{message_id}", summary="Delete a specific message")
async def delete_message(
        message_id: int,  # Assuming message_id is an integer
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),  # Token is automatically extracted from the Authorization header
        current_user: User = Depends(get_current_user)
):
    """
    Endpoint to delete a message by its ID.
    Only the sender can delete a message.
    """
    logging.info(f"Current user attempting to delete a message: {current_user.username}")

    if not current_user:
        logging.error("Current user is None after token validation.")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        await messaging_service.delete_message(message_id, current_user.id, db)
        logging.info(f"Message with ID {message_id} deleted successfully by user {current_user.username}.")
        return {"detail": "Message deleted successfully"}
    except Exception as e:
        logging.error(f"Failed to delete message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")
