"""Demonstrate the usage of OWASPLogger when using the OTel SDK instrumentation.

Given a standard `logger: logging.Logger` which has already been instrumented, and a
`logger_provider` from the OTel instrumentation, you can "upgrade" the logger to an OWASPLogger:

    ```python
    logger_provider.add_log_record_processor(OWASPLogRecordProcessor())
    logger = OWASPLogger(appid=appid, logger=logger)
    ```

In addition to the normal logger functionality, you'll get the methods to log OWASP events:
    ```python
    logger.info("Something has happened")
    logger.authz_admin(admin="banana-bob", user="coconut-charlie")
    ```
"""

import logging

try:
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs import (
        LoggerProvider,
        LoggingHandler,
    )
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
    from opentelemetry.sdk.resources import Resource
except ImportError as e:
    raise ImportError(
        "owasp_logger.otel requires OpenTelemetry dependencies. "
        "Install the library with: pip install owasp-logger[otel]"
    ) from e

from owasp_logger.logger import OWASPLogger
from owasp_logger.otel import OWASPLogRecordProcessor

service_name = "example-service"
appid = "example.appid"


# Instantiate the base Python logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Instrument logging with the OpenTelemetry SDK
resource = Resource.create(attributes={"service.name": service_name})
logger_provider = LoggerProvider(resource=resource)
## Add a batch exporter with output to the console for testing
logger_provider.add_log_record_processor(BatchLogRecordProcessor(ConsoleLogExporter()))
set_logger_provider(logger_provider)
## Attach the OTel LoggingHandler to the base logger
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logger.addHandler(handler)

logger.info("This is what standard OTel logging looks like")


# Transfrom the OTel logger into an OWASPLogger
logger_provider.add_log_record_processor(OWASPLogRecordProcessor())
logger = OWASPLogger(appid=appid, logger=logger)

## logger can now use both standard logging methods and OWASP events directly
logger.info("Messages logged via .info() follow the same format")
logger.authz_admin(
    userid="ananas-alex",
    admin_activity="watered_plants",
    description="Admin ananas-alex watered their plants",
)
## Possibly adding optional parameters
logger.sensitive_read(
    userid="date-delilah",
    obj="scroll",
    description="User date-delilah read the secret scroll",
    hostname="secret.scroll.com",
    port=1234,
    request_uri="http://secret.scroll.com/read/the/secret",
    request_method="GET",
)
