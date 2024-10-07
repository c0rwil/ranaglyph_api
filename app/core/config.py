from pydantic_settings import BaseSettings
from pydantic import Field
import os
from base64 import b64decode
from dotenv import load_dotenv
from app.key_generation import generate_and_write_encryption_key, generate_and_write_jwt_secret_key

generate_and_write_encryption_key()
generate_and_write_jwt_secret_key()

# Reload environment variables to ensure the new keys are loaded
load_dotenv()


# Updated Settings Class
from pydantic_settings import BaseSettings
from pydantic import Field
from base64 import b64decode

class Settings(BaseSettings):
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    algorithm: str = "HS256"
    encryption_key: bytes

    class Config:
        env_file = ".env"
        from_attributes = True
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Decode the base64 encoded encryption key
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY is missing from the environment")

        # Ensure proper padding for the base64 encoded key
        missing_padding = len(encryption_key) % 4
        if missing_padding:
            encryption_key += "=" * (4 - missing_padding)

        self.encryption_key = b64decode(encryption_key)

# Instantiate settings
settings = Settings()