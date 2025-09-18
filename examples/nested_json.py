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
logger.authz_admin(admin="banana-bob", user="coconut-charlie")
logger.authn_login_fail(user="ananas-alex")
logger.authn_login_fail_max(user="ananas-alex", fail_limit=3)
