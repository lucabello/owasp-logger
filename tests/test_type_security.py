import json
import logging

from owasp_logger import OWASPLogger
from owasp_logger.model import NESTED_JSON_KEY, OWASPLogEvent


class TestOWASPLogEventTypeField:
    """Ensure all OWASP log events include type='security'."""

    def test_type_field_in_dataclass(self):
        event = OWASPLogEvent(
            datetime="2026-01-01T00:00:00+00:00",
            type="security",
            appid="test.app",
            event="test_event",
            level="INFO",
        )
        assert event.type == "security"

    def test_type_field_in_dict(self):
        event = OWASPLogEvent(
            datetime="2026-01-01T00:00:00+00:00",
            type="security",
            appid="test.app",
            event="test_event",
            level="INFO",
        )
        d = event.to_dict()
        assert d["type"] == "security"

    def test_type_field_in_json(self):
        event = OWASPLogEvent(
            datetime="2026-01-01T00:00:00+00:00",
            type="security",
            appid="test.app",
            event="test_event",
            level="INFO",
        )
        parsed = json.loads(event.to_json())
        assert parsed["type"] == "security"

    def test_type_field_in_nested_json(self):
        event = OWASPLogEvent(
            datetime="2026-01-01T00:00:00+00:00",
            type="security",
            appid="test.app",
            event="test_event",
            level="INFO",
        )
        parsed = json.loads(event.to_json(nested_json_key=NESTED_JSON_KEY))
        assert parsed[NESTED_JSON_KEY]["type"] == "security"

    def test_type_field_order_in_dict(self):
        """Verify 'type' appears right after 'datetime' in the serialized output."""
        event = OWASPLogEvent(
            datetime="2026-01-01T00:00:00+00:00",
            type="security",
            appid="test.app",
            event="test_event",
            level="INFO",
        )
        keys = list(event.to_dict().keys())
        assert keys[0] == "datetime"
        assert keys[1] == "type"


class TestOWASPLoggerEmitsType:
    """Ensure the OWASPLogger methods produce logs with type='security'."""

    def test_log_event_contains_type_security(self, caplog):
        logger = OWASPLogger(appid="test.app")
        with caplog.at_level(logging.DEBUG):
            logger.authn_login_success(userid="alice")
        assert len(caplog.records) == 1
        record = caplog.records[0]
        owasp_event = getattr(record, NESTED_JSON_KEY, None)
        assert owasp_event is not None
        assert owasp_event["type"] == "security"
        parsed = json.loads(record.getMessage())
        assert parsed[NESTED_JSON_KEY]["type"] == "security"

    def test_multiple_event_types_contain_type_security(self, caplog):
        logger = OWASPLogger(appid="test.app")
        with caplog.at_level(logging.DEBUG):
            logger.authn_login_fail(userid="bob")
            logger.authz_fail(userid="bob", resource="/admin")
            logger.sys_crash(reason="oom")
            logger.session_created(userid="carol")
        for record in caplog.records:
            owasp_event = getattr(record, NESTED_JSON_KEY, None)
            assert owasp_event is not None
            assert owasp_event["type"] == "security"
