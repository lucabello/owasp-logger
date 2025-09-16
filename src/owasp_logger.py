import logging
import json
from datetime import datetime, timezone
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class LogEvent(BaseModel):
    datetime: str = Field(description="ISO8601 timestamp with timezone")
    appid: str
    event: str = Field(description="The type of event being logged (i.e. sys_crash)")
    level: str = Field(description="Log level reflecting the importance of the event")
    description: str = Field(description="Human-readable description of the event being logged")
    # useragent: str
    # source_ip: str = Field(description="IP Address from which the event originated")
    # host_ip: str
    # hostname: str
    # protocol: Literal["http", "https", "grpc"]
    # port: int
    # request_uri: str
    # request_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    # region: str
    # geo: str

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)


class OWASPLogger(logging.Logger):
    def __init__(
        self, appid: str, type: str = "security", name: str = __name__, level: int = logging.INFO
    ):
        """OWASP-compliant logger.

        Args:

        """
        super().__init__(name, level)
        self.appid = appid

        # Add default handler if none exists
        if not self.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.addHandler(handler)

    def _log_event(self, event: str, level: int, description: str):
        log = LogEvent(
            datetime=datetime.now(timezone.utc).astimezone().isoformat(),
            appid=self.appid,
            event=event,
            level=logging.getLevelName(level),
            description=description,
        )
        self.log(level, log.to_json())

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
