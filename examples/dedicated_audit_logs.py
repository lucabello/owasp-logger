"""Demonstrate the usage of OWASPLogger for a dedicated audit log file."""

import logging
from owasp_logger.logger import OWASPLogger

appid = "example.appid"


# Assuming you already have a configured Python logger
logging.basicConfig(format="%(message)s", level=logging.INFO)

# Instead of:
logger = logging.getLogger(__name__)
# You can use:
logger = OWASPLogger(appid=appid)


# The familiar logger functions are just the same
logger.info("Hello World!")

# Emit some OWASP-compliant logs
logger.authn_login_success(userid="bob", description="hello", source_ip="aaaa")
# logger.authz_admin(admin="banana-bob", userid="coconut-charlie", event="something")

# logger.authn_login_fail(userid="ananas-alex")
# logger.authn_login_fail_max(userid="ananas-alex", maxlimit=3)
