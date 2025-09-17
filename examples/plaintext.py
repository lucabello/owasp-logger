"""Demonstrate the usage of OWASPLogger when using a basic plaintext Python logger."""

import logging
from owasp_logger.logger import OWASPLogger

appid = "example.appid"


# Instantiate the base Python logger
logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("This is what plain Python logs look like")


# Transform the Python logger into an OWASPLogger
logger = OWASPLogger(appid=appid)

## logger can now use both standard logging methods and OWASP events directly
logger.info("Messages logged via .info() follow the same format")
logger.authz_admin(admin="banana-bob", user="coconut-charlie")
