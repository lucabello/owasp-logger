import logging
from datetime import datetime, timezone
from typing import List, Optional
from owasp_logger.model import NESTED_JSON_KEY, OWASPLogEvent


class OWASPLogger:
    def __init__(self, appid: str, logger: Optional[logging.Logger] = None):
        """OWASP-compliant logger."""
        self.appid = appid
        self.logger = logger or logging.getLogger(__name__)

    def __getattr__(self, item):
        """Delegate standard logging functions to the internal logger."""
        return getattr(self.logger, item)

    def _log_event(self, event: str, level: int, description: str):
        """Emit an OWASP-compliant log."""
        log = OWASPLogEvent(
            datetime=datetime.now(timezone.utc).astimezone().isoformat(),
            appid=self.appid,
            event=event,
            level=logging.getLevelName(level),
            description=description,
        )
        self.logger.log(level, log.to_json(), extra={NESTED_JSON_KEY: log.to_dict()})

    def authn_login_successafterfail(self, user: str, failures: int):
        """Authentication: successful login."""
        event = f"authn_login_successafterfail:{user},{failures}"
        description = f"User {user} login successfully after {failures} failures"
        self._log_event(event, logging.INFO, description)

    def authn_login_fail(self, user: str):
        """Authentication: failed login."""
        event = f"authn_login_fail:{user}"
        description = f"User {user} login failed"
        self._log_event(event, logging.WARN, description)

    def authn_login_fail_max(self, user: str, fail_limit: int):
        """Authentication: failed login limit reached."""
        event = f"authn_login_fail_max:{user},{fail_limit}"
        description = f"User {user} reached the login fail limit of {fail_limit}"
        self._log_event(event, logging.WARN, description)

    def authn_login_lock(self, user: str):
        """Authentication: account lockout due to multiple failed logins."""
        event = f"authn_login_lock:{user},maxretries"
        description = f"User {user} login locked because maxretries exceeded"
        self._log_event(event, logging.WARN, description)

    def authn_password_change(self, user: str):
        """Authentication: password change was successful."""
        event = f"authn_password_change:{user}"
        description = f"User {user} has successfully changed their password"
        self._log_event(event, logging.INFO, description)

    def authn_password_change_fail(self, user: str):
        """Authentication: password change failed."""
        event = f"authn_password_change_fail:{user}"
        description = f"User {user} failed to change their password"
        self._log_event(event, logging.CRITICAL, description)

    def authn_token_created(self, user: str, permissions: List[str]):
        """Authentication: token created."""
        event = f"authn_token_created:{user},{','.join(permissions)}"
        description = f"A token has been created for {user} with {','.join(permissions)}"
        self._log_event(event, logging.INFO, description)

    def authn_token_revoked(self, user: str, token_id: str):
        """Authentication: token revoked."""
        event = f"authn_token_revoked:{user},{token_id}"
        description = f"Token ID: {token_id} was revoked for user {user}"
        self._log_event(event, logging.INFO, description)

    def authn_token_delete(self, user: str):
        """Authentication: token deleted."""
        event = f"authn_token_delete:{user}"
        description = f"The token for {user} has been deleted"
        self._log_event(event, logging.WARN, description)

    def authz_fail(self, user: str):
        """Authorization: unauthorized access request."""
        event = f"authz_fail:{user},resource"
        description = f"User {user} attempted to access a resource without entitlement"
        self._log_event(event, logging.CRITICAL, description)

    def authz_admin(self, admin: str, user: str):
        """Authorization: administrative activity (user privilege change)."""
        event = f"authz_admin:{user},user_privilege_change"
        description = (
            f"Administrator {admin} has updated privileges of user {user} from user to admin"
        )
        self._log_event(event, logging.WARN, description)

    def sys_startup(self, user: str):
        """System: startup."""
        event = f"sys_startup:{user}"
        description = f"User {user} spawned a new instance"
        self._log_event(event, logging.WARN, description)

    def sys_shutdown(self, user: str):
        """System: shutdown."""
        event = f"sys_shutdown:{user}"
        description = f"User {user} stopped this instance"
        self._log_event(event, logging.WARN, description)

    def sys_restart(self, user: str):
        """System: restart."""
        event = f"sys_restart:{user}"
        description = f"User {user} initiated a restart"
        self._log_event(event, logging.WARN, description)

    def sys_crash(self, reason: str):
        """System: crash."""
        event = f"sys_crash:{reason}"
        description = f"The system crashed due to {reason} error"
        self._log_event(event, logging.WARN, description)

    def sys_monitor_disabled(self, user: str, service: str):
        """System: monitoring disabled."""
        event = f"sys_monitor_disabled:{user},{service}"
        description = f"User {user} has disabled {service}"
        self._log_event(event, logging.WARN, description)

    def user_created(self, admin: str, user: str, permissions: List[str]):
        """User: created.

        Args:
            admin: user who is creating a new user
            user: user being created
            permission: list of permissions for the created user
        """
        event = f"user_created:{admin},{user},{','.join(permissions)}"
        description = (
            f"User {admin} created {user} with {','.join(permissions)} privilege attributes"
        )
        self._log_event(event, logging.WARN, description)

    def user_updated(self, admin: str, user: str, permissions: List[str]):
        """User: created.

        Args:
            admin: user who is creating a new user
            user: user being created
            permission: list of permissions for the created user
        """
        event = f"user_created:{admin},{user},{','.join(permissions)}"
        description = (
            f"User {admin} updated {user} with {','.join(permissions)} privilege attributes"
        )
        self._log_event(event, logging.WARN, description)
