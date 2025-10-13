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
logger.authz_admin(userid="ananas-alex", admin_activity="watered_plants")
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
