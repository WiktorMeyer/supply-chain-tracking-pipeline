import httpx
import time

from src.ingestion import classifier
from src.ingestion.exceptions import PermanentFetchError, TransientFetchError

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

# How many seconds before expiry to proactively refresh the token.
TOKEN_REFRESH_MARGIN = 30


class TokenManager:
    def __init__(self, client_id: str, client_secret: str, client: httpx.Client):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = client
        self.token = None
        self.expires_at = None

    def get_token(self):
        """Return a valid access token, refreshing automatically if needed."""
        if self.token and self.expires_at and time.monotonic() < self.expires_at:
            return self.token
        return self._refresh()

    def invalidate(self):
        """Forget the current token"""
        self.token = None
        self.expires_at = None

    def force_refresh(self):
        """Invalidate the current token and fetch a new one"""
        self.invalidate()
        return self._refresh()

    def _refresh(self):
        """Fetch a new access token from the OpenSky authentication server."""
        try:
            r = self.client.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
        except httpx.RequestError as exc:
            raise classifier.classify_exception(exc) from exc
        if r.status_code == 401:
            raise PermanentFetchError("Invalid OpenSky client credentials (401)")

        data = classifier.classify_response(r)
        try:
            self.token = data["access_token"]
        except KeyError as exc:
            raise TransientFetchError("Missing access_token in OIDC response") from exc
        expires_in = data.get("expires_in", 1800)
        self.expires_at = time.monotonic() + (expires_in - TOKEN_REFRESH_MARGIN)
        return self.token

    def headers(self):
        """Return request headers with a valid Bearer token."""
        return {"Authorization": f"Bearer {self.get_token()}"}