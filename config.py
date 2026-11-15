import os
from dataclasses import dataclass
from dotenv import load_dotenv


def _get_str(key: str, default=None, required=False) -> str | None:
    value = os.environ.get(key, None)
    if value is None or value.strip() == "":
        if required:
            raise ValueError(f"Missing required environment variable: {key}")
        return default
    return value.strip()

def _get_int(key: str, default=None, required=False) -> int | None:
    value = _get_str(key, default, required)
    if value is None:
        return default
    try:
        value = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {key}: {value}") from exc
    return value

def _get_float(key: str, default=None, required=False) -> float | None:
    value = _get_str(key, default, required)
    if value is None:
        return default
    try :
        value = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid float for {key}: {value}") from exc
    return value

@dataclass(frozen=True)
class Settings:
    opensky_base_url: str | None
    client_id: str | None
    client_secret: str | None
    bbox_lamin: float
    bbox_lomin: float
    bbox_lamax: float
    bbox_lomax: float
    poll_interval_sec: int
    connect_timeout_sec: float
    read_timeout_sec: float

    def __post_init__(self)-> None:
        if not (self.bbox_lamin < self.bbox_lamax):
            raise ValueError("lamin is > lomax")
        if not self.bbox_lomin < self.bbox_lomax:
            raise ValueError("lomin is > lomax")
        if  not self.poll_interval_sec > 0:
            raise ValueError("poll_interval_sec must be greater than 0")
        if  not self.connect_timeout_sec > 0 :
            raise ValueError("connect_timeout_sec must be greater than 0")
        if not self.read_timeout_sec > 0:
            raise ValueError("read_timeout_sec must be greater than 0")
        if bool(self.client_id) != bool(self.client_secret):
            raise ValueError(
                "Both OPENSKY_CLIENT_ID and OPENSKY_CLIENT_SECRET must be set together, or both left empty."
            )
    @property
    def bbox_params(self) -> dict[str, float | None]:
        return {
            "lamin": self.bbox_lamin,
            "lomin": self.bbox_lomin,
            "lamax": self.bbox_lamax,
            "lomax": self.bbox_lomax,
        }

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        return cls(
            opensky_base_url=_get_str("OPENSKY_BASE_URL", required = True),
            client_id=_get_str("CLIENT_ID"),
            client_secret=_get_str("CLIENT_SECRET"),
            bbox_lamin=_get_float("BBOX_LAMIN", required = True, default = 50.7),
            bbox_lomin=_get_float("BBOX_LOMIN", required = True, default = 3.3),
            bbox_lamax=_get_float("BBOX_LAMAX", required = True, default = 53.6),
            bbox_lomax=_get_float("BBOX_LOMAX", required = True, default = 7.2),
            poll_interval_sec = _get_int("POLL_INTERVAL_SEC", default=20),
            connect_timeout_sec = _get_float("CONNECT_TIMEOUT_SEC", default=5.0),
            read_timeout_sec = _get_float("READ_TIMEOUT_SEC", default=15.0),
        )

settings = Settings.from_env()
