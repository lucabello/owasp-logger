import logging
from datetime import datetime, timezone
from typing import List, Literal, Optional

from typing_extensions import Unpack

from owasp_logger.model import NESTED_JSON_KEY, OWASPLogEvent, OWASPLogMetadata


class OWASPLogger:
    """Logger for OWASP security events.

    Implement a method for each security event listed by OWASP:
    https://cheatsheetseries.owasp.org/cheatsheets/Logging_Vocabulary_Cheat_Sheet.html
    """

    def __init__(self, appid: str, logger: Optional[logging.Logger] = None):
        """OWASP-compliant logger."""
        self.appid = appid
        self.logger = logger or logging.getLogger(__name__)

    def __getattr__(self, item):
        """Delegate standard logging functions to the internal logger."""
        return getattr(self.logger, item)

    def _log_event(self, event: str, level: int, metadata: OWASPLogMetadata):
        """Emit an OWASP-compliant log."""
        log = OWASPLogEvent(
            datetime=datetime.now(timezone.utc).astimezone().isoformat(),
            appid=self.appid,
            event=event,
            level=logging.getLevelName(level),
            **metadata,
        )
        self.logger.log(level, log.to_json(), extra={NESTED_JSON_KEY: log.to_dict()})

    # Authentication

    def authn_login_success(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a successful login event."""
        event = f"authn_login_success:{userid}"
        self._log_event(event, logging.INFO, metadata)

    def authn_login_successafterfail(
        self, userid: str, retries: int, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a successful login event after previously failing."""
        event = f"authn_login_successafterfail:{userid},{retries}"
        self._log_event(event, logging.INFO, metadata)

    def authn_login_fail(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a failed login event."""
        event = f"authn_login_fail:{userid}"
        self._log_event(event, logging.WARN, metadata)

    def authn_login_fail_max(
        self, userid: str, maxlimit: int, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record the failed login limit being reached."""
        event = f"authn_login_fail_max:{userid},{maxlimit}"
        self._log_event(event, logging.WARN, metadata)

    def authn_login_lock(
        self, userid: str, reason: str = "maxretries", **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record an account lockout (e.g., due to multiple failed logins)."""
        event = f"authn_login_lock:{userid},{reason}"
        self._log_event(event, logging.WARN, metadata)

    def authn_password_change(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a successful password change event."""
        event = f"authn_password_change:{userid}"
        self._log_event(event, logging.INFO, metadata)

    def authn_password_change_fail(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a failed password changed event."""
        event = f"authn_password_change_fail:{userid}"
        self._log_event(event, logging.CRITICAL, metadata)

    def authn_impossible_travel(
        self, userid: str, region1: str, region2: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a user logged in from one city suddenly appearing in another, too far away.

        This often indicates a potential account takeover.
        """
        event = f"authn_impossible_travel:{userid},{region1},{region2}"
        self._log_event(event, logging.CRITICAL, metadata)

    def authn_token_created(
        self, userid: str, entitlements: List[str], **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a token creation."""
        event = f"authn_token_created:{userid},{','.join(entitlements)}"
        self._log_event(event, logging.INFO, metadata)

    def authn_token_revoked(self, userid: str, tokenid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a token being revoked for a given account."""
        event = f"authn_token_revoked:{userid},{tokenid}"
        self._log_event(event, logging.INFO, metadata)

    def authn_token_reuse(self, userid: str, tokenid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record that a previously revoked token was attempted to be reused."""
        event = f"authn_token_reuse:{userid},{tokenid}"
        self._log_event(event, logging.CRITICAL, metadata)

    def authn_token_delete(self, appid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a token deletion."""
        event = f"authn_token_delete:{appid}"
        self._log_event(event, logging.WARN, metadata)

    # Authorization

    def authz_fail(self, userid: str, resource: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record an attempt to access an unauthorized resource."""
        event = f"authz_fail:{userid},{resource}"
        self._log_event(event, logging.CRITICAL, metadata)

    def authz_change(
        self,
        userid: str,
        from_entitlement: str,
        to_entitlement: str,
        **metadata: Unpack[OWASPLogMetadata],
    ):
        """Record the user or entity entitlements being changed."""
        event = f"authz_change:{userid},{from_entitlement},{to_entitlement}"
        self._log_event(event, logging.WARNING, metadata)

    def authz_admin(
        self,
        userid: str,
        admin_activity: str,
        **metadata: Unpack[OWASPLogMetadata],
    ):
        """Record any administrative activity (e.g., user privilege change)."""
        event = f"authz_admin:{userid},{admin_activity}"
        self._log_event(event, logging.WARN, metadata)

    # Encryption

    def crypt_decrypt_fail(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record the failure to perform a decryption.

        Args:
            userid: the user failing the decryption
            error: a human-readable reason why the decryption failed
        """
        event = f"crypt_decrypt_fail:{userid}"
        self._log_event(event, logging.WARN, metadata)

    def crypt_encrypt_fail(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record the failure to perform an encryption

        Args:
            userid: the user failing the encryption
            error: a human-readable reason why the encryption failed
        """
        event = f"crypt_encrypt_fail:{userid}"
        self._log_event(event, logging.WARN, metadata)

    # Excessive use

    def excess_rate_limit_exceeded(
        self, userid: str, max: int, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record the expected service limit ceiling being reached."""
        event = f"excess_rate_limit_exceeded:{userid},{str(max)}"
        self._log_event(event, logging.WARN, metadata)

    # File upload

    def upload_complete(
        self, userid: str, filename: str, type: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a successful file upload."""
        event = f"upload_complete:{userid},{filename},{type}"
        self._log_event(event, logging.INFO, metadata)

    def upload_stored(
        self, filename: str, src: str, dst: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record that a file was stored successfully."""
        event = f"upload_stored:{filename},{src},{dst}"
        self._log_event(event, logging.INFO, metadata)

    def upload_validation(
        self,
        filename: str,
        validator: str,
        status: Literal["FAILED", "incomplete", "passed"],
        **metadata: Unpack[OWASPLogMetadata],
    ):
        """Record the result of a file validation process."""
        event = f"upload_validation:{filename},{validator}:{status}"
        level = logging.CRITICAL if status == "FAILED" else logging.INFO
        self._log_event(event, level, metadata)

    def upload_delete(self, userid: str, fileid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a file deletion event."""
        event = f"upload_delete:{userid},{fileid}"
        self._log_event(event, logging.INFO, metadata)

    # Input Validation

    def input_validation_fail(
        self, fields: List[str], userid: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a general input validation failure."""
        event = f"input_validation_fail:({','.join(fields)}),{userid}"
        self._log_event(event, logging.WARNING, metadata)

    def input_validation_discrete_fail(
        self, field: str, userid: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a discrete field validation failure."""
        event = f"input_validation_discrete_fail:{field},{userid}"
        self._log_event(event, logging.WARNING, metadata)

    # Malicious Behavior

    def malicious_excess_404(
        self, user_or_ip: str, useragent: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record excessive 404 errors (possible probing)."""
        event = f"malicious_excess_404:{user_or_ip},{useragent}"
        self._log_event(event, logging.WARNING, metadata)

    def malicious_extraneous(
        self, user_or_ip: str, inputname: str, useragent: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record unexpected input or extraneous data."""
        event = f"malicious_extraneous:{user_or_ip},{inputname},{useragent}"
        self._log_event(event, logging.CRITICAL, metadata)

    def malicious_attack_tool(
        self, user_or_ip: str, toolname: str, useragent: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record detection of attack tool usage."""
        event = f"malicious_attack_tool:{user_or_ip},{toolname},{useragent}"
        self._log_event(event, logging.CRITICAL, metadata)

    def malicious_cors(
        self, user_or_ip: str, useragent: str, referer: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a CORS violation attempt."""
        event = f"malicious_cors:{user_or_ip},{useragent},{referer}"
        self._log_event(event, logging.CRITICAL, metadata)

    def malicious_direct_reference(
        self, user_or_ip: str, useragent: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record a direct object reference attempt."""
        event = f"malicious_direct_reference:{user_or_ip},{useragent}"
        self._log_event(event, logging.CRITICAL, metadata)

    # Privilege Changes

    def privilege_permissions_changed(
        self,
        userid: str,
        obj: str,
        fromlevel: str,
        tolevel: str,
        **metadata: Unpack[OWASPLogMetadata],
    ):
        """Record a permission level change."""
        event = f"privilege_permissions_changed:{userid},{obj},{fromlevel},{tolevel}"
        self._log_event(event, logging.WARNING, metadata)

    # Sensitive Data Changes

    def sensitive_create(self, userid: str, obj: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record creation of a sensitive object."""
        event = f"sensitive_create:{userid},{obj}"
        self._log_event(event, logging.WARNING, metadata)

    def sensitive_read(self, userid: str, obj: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record access (read) of sensitive data."""
        event = f"sensitive_read:{userid},{obj}"
        self._log_event(event, logging.WARNING, metadata)

    def sensitive_update(self, userid: str, obj: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record modification of sensitive data."""
        event = f"sensitive_update:{userid},{obj}"
        self._log_event(event, logging.WARNING, metadata)

    def sensitive_delete(self, userid: str, obj: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record deletion of sensitive data."""
        event = f"sensitive_delete:{userid},{obj}"
        self._log_event(event, logging.WARNING, metadata)

    # Sequence Errors

    def sequence_fail(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a sequence error (unexpected order of actions)."""
        event = f"sequence_fail:{userid}"
        self._log_event(event, logging.CRITICAL, metadata)

    # Session Management

    def session_created(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record session creation."""
        event = f"session_created:{userid}"
        self._log_event(event, logging.INFO, metadata)

    def session_renewed(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record session renewal."""
        event = f"session_renewed:{userid}"
        self._log_event(event, logging.INFO, metadata)

    def session_expired(self, userid: str, reason: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record session expiration."""
        event = f"session_expired:{userid},{reason}"
        self._log_event(event, logging.INFO, metadata)

    def session_use_after_expire(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record attempt to use an expired session."""
        event = f"session_use_after_expire:{userid}"
        self._log_event(event, logging.CRITICAL, metadata)

    # System Events

    def sys_startup(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record system startup event."""
        event = f"sys_startup:{userid}"
        self._log_event(event, logging.WARNING, metadata)

    def sys_shutdown(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record system shutdown event."""
        event = f"sys_shutdown:{userid}"
        self._log_event(event, logging.WARNING, metadata)

    def sys_restart(self, userid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record system restart event."""
        event = f"sys_restart:{userid}"
        self._log_event(event, logging.WARNING, metadata)

    def sys_crash(self, reason: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record a system crash."""
        event = f"sys_crash:{reason}"
        self._log_event(event, logging.WARNING, metadata)

    def sys_monitor_disabled(
        self, userid: str, monitor: str, **metadata: Unpack[OWASPLogMetadata]
    ):
        """Record disabling of a system monitor."""
        event = f"sys_monitor_disabled:{userid},{monitor}"
        self._log_event(event, logging.WARNING, metadata)

    def sys_monitor_enabled(self, userid: str, monitor: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record enabling of a system monitor."""
        event = f"sys_monitor_enabled:{userid},{monitor}"
        self._log_event(event, logging.WARNING, metadata)

    # User Management

    def user_created(
        self,
        userid: str,
        newuserid: str,
        attributes: str,
        **metadata: Unpack[OWASPLogMetadata],
    ):
        """Record creation of a new user."""
        event = f"user_created:{userid},{newuserid},{attributes}"
        self._log_event(event, logging.WARNING, metadata)

    def user_updated(
        self,
        userid: str,
        onuserid: str,
        attributes: str,
        **metadata: Unpack[OWASPLogMetadata],
    ):
        """Record update to a user's attributes."""
        event = f"user_updated:{userid},{onuserid},{attributes}"
        self._log_event(event, logging.WARNING, metadata)

    def user_archived(self, userid: str, onuserid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record archiving of a user."""
        event = f"user_archived:{userid},{onuserid}"
        self._log_event(event, logging.INFO, metadata)

    def user_deleted(self, userid: str, onuserid: str, **metadata: Unpack[OWASPLogMetadata]):
        """Record deletion of a user."""
        event = f"user_deleted:{userid},{onuserid}"
        self._log_event(event, logging.INFO, metadata)
