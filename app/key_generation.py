import secrets
from Crypto.Random import get_random_bytes
from base64 import b64encode
import os
from dotenv import load_dotenv

# Path to the .env file
ENV_FILE_PATH = ".env"

# Function to generate and write the encryption key if it's not already in the .env file
def generate_and_write_encryption_key():
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("ENCRYPTION_KEY="):
                    # ENCRYPTION_KEY already exists, set it in the environment
                    encryption_key = line.split("=")[1].strip()
                    os.environ["ENCRYPTION_KEY"] = encryption_key
                    return

    # Generate a new ENCRYPTION_KEY and encode it in base64
    encryption_key = get_random_bytes(32)
    encoded_key = b64encode(encryption_key).decode()

    # Write the ENCRYPTION_KEY to the .env file
    with open(ENV_FILE_PATH, 'a') as file:
        file.write(f"ENCRYPTION_KEY={encoded_key}\n")

    # Set the ENCRYPTION_KEY in the environment
    os.environ["ENCRYPTION_KEY"] = encoded_key

# Function to generate and write the JWT secret key if it's not already in the .env file
def generate_and_write_jwt_secret_key():
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("JWT_SECRET_KEY="):
                    jwt_secret_key = line.split("=")[1].strip()
                    os.environ["JWT_SECRET_KEY"] = jwt_secret_key
                    return jwt_secret_key

    # Generate a new JWT_SECRET_KEY
    jwt_secret_key = secrets.token_hex(32)

    # Write the JWT_SECRET_KEY to the .env file
    with open(ENV_FILE_PATH, 'a') as file:
        file.write(f"JWT_SECRET_KEY={jwt_secret_key}\n")

    # Set the JWT_SECRET_KEY in the environment
    os.environ["JWT_SECRET_KEY"] = jwt_secret_key
    return jwt_secret_key