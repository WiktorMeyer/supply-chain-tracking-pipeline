class IngestionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class AuthRefreshRequiredError(IngestionError):
    """Signals that the current Bearer token was rejected."""

class TransientFetchError(IngestionError):
    """Signals a temporary network or upstream server fault."""
    def __init__(self, message: str, retry_after: float | None = None):
        IngestionError.__init__(self, message)
        self.retry_after = retry_after

class PermanentFetchError(IngestionError):
    """Signals a non-retryable client or configuration detail"""