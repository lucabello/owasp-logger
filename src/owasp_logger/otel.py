from owasp_logger.model import NESTED_JSON_KEY

try:
    from opentelemetry.sdk._logs import LogData, LogRecordProcessor
except ImportError as e:
    raise ImportError(
        "owasp_logger.otel requires OpenTelemetry dependencies. "
        "Install the library with: pip install owasp-logger[otel]"
    ) from e


class OWASPLogRecordProcessor(LogRecordProcessor):
    """Enrich OTel logs with OWASP-compliant data.

    A processor that inspects LogData coming in from standard logging via OTel LoggingHandler.
    If the original LogRecord has extra OWASP data (under NESTED_JSON_KEY), it serializes it into
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
        # Put description in body
        if isinstance(owasp_event, dict):
            log_record.body = owasp_event.get("description", log_record.body)

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000):
        pass
