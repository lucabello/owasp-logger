"""Demonstrate the usage of OWASPLogger for a dedicated audit log file."""

import logging
from owasp_logger.logger import OWASPLogger

appid = "example.appid"


# Instantiate the base Python logger
logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Transform the Python logger into an OWASPLogger
logger = OWASPLogger(appid=appid)

# Emit some OWASP-compliant logs
logger.authz_admin(admin="banana-bob", user="coconut-charlie")
logger.authn_login_fail(user="ananas-alex")
logger.authn_login_fail_max(user="ananas-alex", fail_limit=3)
