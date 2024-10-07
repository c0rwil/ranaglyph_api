from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from app.sockets.manager import ConnectionManager
from app.db.supabase_client import supabase
from app.core.encryption import decrypt_message, encrypt_message, authenticate_websocket
from jose import jwt, JWTError

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/message/{username}")
async def websocket_message_endpoint(websocket: WebSocket, username: str, token: str):
    # Authenticate the user
    authenticated_username = await authenticate_websocket(token)
    await manager.connect(websocket)

    try:
        while True:
            # Receive data from client
            data = await websocket.receive_json()

            if data['type'] == 'message':
                # Encrypt the message before saving
                plain_content = data['content']
                nonce, ciphertext = encrypt_message(plain_content)

                sender_username = data['sender_username']
                receiver_username = data['receiver_username']

                # Fetch sender and receiver user IDs from Supabase
                sender = supabase.table('users').select('user_id').filter('username', 'eq', sender_username).execute()
                receiver = supabase.table('users').select('user_id').filter('username', 'eq',
                                                                            receiver_username).execute()

                if not sender.get('data') or not receiver.get('data'):
                    raise HTTPException(status_code=404, detail="Sender or receiver not found")

                sender_id = sender['data'][0]['user_id']
                receiver_id = receiver['data'][0]['user_id']

                # Save encrypted message to Supabase
                message_data = {
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'nonce': nonce.hex(),
                    'content': ciphertext.hex(),
                    'timestamp': 'now()',
                    'status': 'sent'
                }
                response = supabase.table('messages').insert(message_data).execute()
                message_id = response['data'][0]['id']

                # Broadcast the message to the relevant client only
                for connection in manager.active_connections:
                    if connection == websocket or connection.client_state == receiver_id:
                        await connection.send_json({
                            'type': 'message',
                            'status': 'sent',
                            'message_id': message_id,
                            'sender_username': sender_username,
                            'receiver_username': receiver_username,
                            'nonce': nonce.hex(),
                            'content': ciphertext.hex(),
                            'timestamp': response['data'][0]['timestamp']
                        })

            elif data['type'] == 'status_update':
                # Handle message status updates (e.g., delivered, seen)
                message_id = data['message_id']
                new_status = data['status']

                # Update the message status in Supabase
                response = supabase.table('messages').update({'status': new_status}).eq('id', message_id).execute()

                if response.get('error'):
                    raise HTTPException(status_code=400, detail="Failed to update message status")

                # Notify relevant clients about the status update
                for connection in manager.active_connections:
                    await connection.send_json({
                        'type': 'status_update',
                        'message_id': message_id,
                        'new_status': new_status
                    })

            elif data['type'] == 'delete_message':
                # Handle deleting a message (unsend/self-destruct)
                message_id = data['message_id']

                # Update the message to mark it as deleted
                response = supabase.table('messages').update({"deleted_at": "now()"}).eq('id', message_id).execute()
                if response.get('error'):
                    raise HTTPException(status_code=400, detail="Failed to delete message")

                # Notify relevant clients to delete the message
                for connection in manager.active_connections:
                    await connection.send_json({
                        'type': 'delete_message',
                        'message_id': message_id
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
