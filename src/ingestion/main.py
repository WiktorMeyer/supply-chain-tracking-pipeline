import os
import httpx
from dotenv import load_dotenv
from token_manager import TokenManager

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
if not client_id or not client_secret:
    raise RuntimeError("Missing CLIENT_ID or CLIENT_SECRET in .env")

tokens = TokenManager(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET"),
    client= httpx.Client(timeout=httpx.Timeout(connect=5.0, read=10.0))
)

