import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
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

from owasp_logger.logger import OWASPLogger
from owasp_logger.otel import OWASPLogRecordProcessor

service_name = "example-service"
appid = "example.appid"

# Instrument logging with the OpenTelemetry SDK
resource = Resource.create(attributes={"service.name": service_name})
provider = LoggerProvider(resource=resource)
# Add our custom processor first
provider.add_log_record_processor(OWASPLogRecordProcessor())
# Then add a batch exporter (for example to console) for testing
provider.add_log_record_processor(BatchLogRecordProcessor(ConsoleLogExporter()))

# 2. Set the global provider
# Note: In OTel, you may need opentelemetry._logs.set_logger_provider(provider)

set_logger_provider(provider)

# 3. Attach the OTel LoggingHandler to the root logger (or whichever logger you prefer)
handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
# Optionally use JSON formatter on this handler if you want textual logs locally
# But the OTel handler ultimately exports via exporters
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# # 4. Return your helper wrapper
owasp_logger = OWASPLogger(appid=appid, logger=logging.getLogger(service_name))

logger.info("What?")
owasp_logger.authz_admin(admin="banana-bob", user="coconut-charlie")
