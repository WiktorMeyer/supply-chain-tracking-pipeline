import os
from dotenv import load_dotenv
from token_manager import TokenManager

load_dotenv()

tokens = TokenManager(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET"),
)

