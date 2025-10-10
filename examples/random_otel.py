"""Emit a random set of OWASP Logs for testing purposes."""

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

import random

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

# Transfrom the OTel logger into an OWASPLogger
logger_provider.add_log_record_processor(OWASPLogRecordProcessor())
logger = OWASPLogger(appid=appid, logger=logger)


def random_bool():
    return random.choice([True, False])


if random_bool():
    for i in range(1, random.randint(1, 5)):
        logger.authz_admin(
            userid="ananas-alex",
            admin_activity="watered_plants",
            description="Admin anans-alex watered their plants",
        )
if random_bool():
    for i in range(1, random.randint(1, 5)):
        logger.authn_impossible_travel(userid="banana-bob", region1="office", region2="beach")
if random_bool():
    for i in range(1, random.randint(1, 5)):
        logger.malicious_extraneous(
            user_or_ip="coconut-charlie", inputname="palmtree", useragent="CoconutBrowser 1.0"
        )
if random_bool():
    for i in range(1, random.randint(1, 5)):
        logger.sensitive_read(
            userid="date-delilah",
            obj="scroll",
            description="User date-delilah read the secret scroll",
            hostname="secret.scroll.com",
            port=1234,
            request_uri="http://secret.scroll.com/read/the/secret",
            request_method="GET",
        )
