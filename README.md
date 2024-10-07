# Ranaglyph 

A secure messaging app built with FastAPI, supporting end-to-end encryption, token-based authentication, real-time messaging via WebSockets, and integration with Supabase for database operations.

## Features

- **End-to-End Encryption**: Messages are encrypted on the client side and only decrypted on the recipient's device.
- **Real-Time Messaging**: Real-time communication is supported via WebSockets.
- **JWT Authentication**: Secure authentication with JSON Web Tokens (JWT).
- **Message Management**: Users can delete (unsend) messages, and messages can also self-destruct.
- **Supabase Integration**: Supabase is used as the backend database to manage users and messages.

## Project Structure



## Requirements

1. **Python 3.8+**
2. **Supabase Account**: Set up a Supabase account and create a project to obtain the `SUPABASE_URL` and `SUPABASE_KEY`.

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/fastapi_messaging_app.git
cd fastapi_messaging_app

pip install .

Create a .env file in the root directory:

env

SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
JWT_SECRET_KEY=your_generated_secret_key_here