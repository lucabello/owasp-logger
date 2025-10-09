import json
from dataclasses import asdict, dataclass
from typing import Dict, Literal, Optional, TypedDict

NESTED_JSON_KEY = "owasp_event"


@dataclass
class OWASPLogEvent:
    datetime: str  # ISO8601 timestamp with timezone
    appid: str
    event: str  # The type of event being logged (i.e. sys_crash)
    level: str  # Log level reflecting the importance of the event
    description: Optional[str] = None  # Human-readable description of the event being logged
    source_ip: Optional[str] = None  # IP Address from which the event originated
    host_ip: Optional[str] = None
    hostname: Optional[str] = None
    protocol: Optional[Literal["http", "https", "grpc"]] = None
    port: Optional[int] = None
    request_uri: Optional[str] = None
    request_method: Optional[Literal["GET", "POST", "PUT", "PATCH", "DELETE"]] = None
    region: Optional[str] = None
    geo: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self) -> Dict:
        log_event = asdict(self)
        return {k: v for k, v in log_event.items() if v is not None}


class OWASPLogMetadata(TypedDict, total=False):
    description: str
    source_ip: str
    host_ip: str
    hostname: str
    protocol: Literal["http", "https", "grpc"]
    port: int
    request_uri: str
    request_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    region: str
    geo: str
