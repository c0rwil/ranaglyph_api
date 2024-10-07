from datetime import datetime
from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.message import Message as MessageModel  # Ensure your Message model is imported
from app.schemas.message import MessageCreate, MessageResponse
import logging

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MessagingService:

    def construct_message_response(self, message_data: MessageModel) -> MessageResponse:
        """
        Helper method to construct a MessageResponse from database model instance.
        """
        logger.debug(f"Constructing MessageResponse from data: {message_data}")
        return MessageResponse(
            id=message_data.id,
            sender_id=message_data.sender_id,
            receiver_id=message_data.receiver_id,
            content=message_data.content,
            timestamp=message_data.timestamp
        )

    async def send_message(self, message_data: MessageCreate, db: Session = Depends(get_db)) -> MessageResponse:
        try:
            # Prepare message data for storage
            logger.info(
                f"Attempting to send message from user {message_data.sender_id} to user {message_data.receiver_id}")
            new_message = MessageModel(
                sender_id=message_data.sender_id,
                receiver_id=message_data.receiver_id,
                content=message_data.content,
                timestamp=datetime.utcnow().isoformat(),
                status="sent"  # Set default status to "sent"
            )

            # Add new message to the database
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # Construct and return a response object
            logger.info(
                f"Message sent successfully from user {message_data.sender_id} to user {message_data.receiver_id}")
            return self.construct_message_response(new_message)

        except Exception as e:
            error_msg = f"Failed to send message: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

    async def get_messages(self, sender_id: int, receiver_id: int, db: Session) -> List[MessageResponse]:
        """
        Retrieve messages between a sender and a receiver.
        """
        try:
            logger.info(f"Attempting to retrieve messages between user {sender_id} and user {receiver_id}")

            # Query messages involving the sender and receiver
            messages = db.query(MessageModel).filter(
                (MessageModel.sender_id == sender_id) | (MessageModel.receiver_id == receiver_id)
            ).order_by(MessageModel.timestamp).all()

            logger.info(f"Retrieved {len(messages)} messages between user {sender_id} and user {receiver_id}")
            return [self.construct_message_response(message) for message in messages]

        except Exception as e:
            error_msg = f"Failed to retrieve messages: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

    async def delete_message(self, message_id: int, user_id: int, db: Session):
        """
        Delete a specific message if the user is the sender.
        """
        try:
            logger.info(f"User {user_id} attempting to delete message {message_id}")

            # Check if the user is the sender of the message
            message = db.query(MessageModel).filter(MessageModel.id == message_id).first()

            if not message:
                error_msg = "Message not found."
                logger.warning(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)

            if message.sender_id != user_id:
                error_msg = "You are not authorized to delete this message."
                logger.warning(error_msg)
                raise HTTPException(status_code=403, detail=error_msg)

            # Delete the message
            db.delete(message)
            db.commit()

            logger.info(f"Message {message_id} deleted successfully by user {user_id}")

        except Exception as e:
            error_msg = f"Failed to delete message: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
