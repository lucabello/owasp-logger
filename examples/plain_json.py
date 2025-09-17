import logging
from owasp_logger.logger import OWASPLogger

appid = "example.appid"


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# # 4. Return your helper wrapper
owasp_logger = OWASPLogger(appid=appid, logger=logger)

owasp_logger.authz_admin(admin="banana-bob", user="coconut-charlie")
