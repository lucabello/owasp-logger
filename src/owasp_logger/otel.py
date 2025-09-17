import json

from opentelemetry import trace
from opentelemetry.sdk._logs import (
    LogData,
    LoggerProvider,
    LoggingHandler,
    LogRecord,
    LogRecordProcessor,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import get_current_span

from owasp_logger.model import NESTED_JSON_KEY, OWASPLogEvent


class OWASPLogRecordProcessor(LogRecordProcessor):
    """
    A processor that inspects LogData coming in from standard logging via OTel LoggingHandler.
    If the original LogRecord had an `owasp_event` extra (our model), it serializes it into
    the OTel body or into attributes, so that the downstream exporter sees structured data.
    """

    def emit(self, log_data: LogData) -> None:
        """
        Modify the log_data in place before it's exported.
        """
        # The log_data has `log_record`, which has attributes like .body, .attributes, etc.
        log_record = log_data.log_record
        attributes = log_record.attributes or {}
        owasp_event = attributes.get(NESTED_JSON_KEY)
        if isinstance(owasp_event, dict):
            # Put description in body
            log_record.body = owasp_event.get("description", log_record.body)

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000):
        pass
