from typing import Dict
from pydantic import BaseModel, Field

NESTED_JSON_KEY = "owasp_event"


class OWASPLogEvent(BaseModel):
    datetime: str = Field(description="ISO8601 timestamp with timezone")
    appid: str
    event: str = Field(description="The type of event being logged (i.e. sys_crash)")
    level: str = Field(description="Log level reflecting the importance of the event")
    description: str = Field(description="Human-readable description of the event being logged")
    # useragent: str
    # source_ip: str = Field(description="IP Address from which the event originated")
    # host_ip: str
    # hostname: str
    # protocol: Literal["http", "https", "grpc"]
    # port: int
    # request_uri: str
    # request_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    # region: str
    # geo: str

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)

    def to_dict(self) -> Dict:
        return self.model_dump(exclude_none=True)
