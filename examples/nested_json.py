"""Demonstrate the usage of OWASPLogger for a custom logger that re-uses the OWASP information.

This examples shows how an application developer can provide their own logging.Formatter to the
OWASPLogger class, ensuring they can manipulate the OWASP information and output the logs in any
desired way.

One use case is nested JSON: when the application is already emitting JSON logs, the dev might
want to integrate the OWASP information as a nested json field. This example shows how to achieve
that.
"""

import json
import logging

from owasp_logger.logger import OWASPLogger
from owasp_logger.model import NESTED_JSON_KEY


class NestedJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Extract the OWASP information
        owasp_event = getattr(record, NESTED_JSON_KEY, {})
        # Define the output shape of your logs
        payload = {
            "logger": record.name,
            "level": record.levelname,
            "message": owasp_event.get("description") or record.getMessage(),
        }
        if owasp_event:
            payload[NESTED_JSON_KEY] = owasp_event

        return json.dumps(payload)


# Instantiate the base Python logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add the NestedJSONFormatter to the logger
handler = logging.StreamHandler()
handler.setFormatter(NestedJSONFormatter())
logger.addHandler(handler)

# Transform the Python logger into an OWASPLogger
logger = OWASPLogger(appid="nestedjson.app", logger=logger)

# Emit some OWASP-compliant logs
logger.info("Did I just get coconut-malled?")
logger.authz_admin(
    userid="ananas-alex",
    admin_activity="watered_plants",
    description="Admin ananas-alex watered their plants",
)
## Possibly adding optional parameters
logger.authn_login_success(userid="banana-bob", description="hello", source_ip="10.1.2.3")
logger.crypt_decrypt_fail(
    userid="coconut-charlie", description="User coconut-charlie failed to decrypt some file"
)
logger.sensitive_read(
    userid="date-delilah",
    obj="scroll",
    description="User date-delilah read the secret scroll",
    hostname="secret.scroll.com",
    port=1234,
    request_uri="http://secret.scroll.com/read/the/secret",
    request_method="GET",
)
