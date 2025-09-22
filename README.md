# OWASP Logger

Example usage:

```
# Set up the environment
uv sync --group dev
source .venv/bin/activate

# Check out the examples
python examples/otel.py

# Try the logger from the Python shell
python
>>> from src.owasp_logger.logger import OWASPLogger
>>> logger = OWASPLogger(appid="coconut.app")
>>> logger.authn_login_lock(user="bob")
{"datetime":"2025-09-16T17:04:34.128037+02:00","appid":"coconut.app","event":"authn_login_lock:bob,maxretries","level":"WARNING","description":"User bob login locked because maxretries exceeded"}
```

## Getting OWASP logs in Loki

To get your logs into Loki, we recommend using an OpenTelemetry Collector (charm or snap, depending on your needs).

```mermaid
flowchart LR
    openstack[Openstack]
    sunbeam[Sunbeam]
    landscape
    cloud-init
    something[Something using OTel SDK + OWASPLogger]
    cos-proxy
    otelcol-snap[OpenTelemetry Collector **Snap**]
    otelcol-charm[OpenTelemetry Collector **Charm**]
    loki2[Loki 2]
    loki3[Loki 3]

    openstack --> cos-proxy
    sunbeam --> otelcol-charm
    landscape --> otelcol-snap
    cloud-init --> otelcol-snap
    something --> loki3

    cos-proxy --> otelcol-charm
    otelcol-snap --> loki3
    otelcol-charm -->|OTLP Format| loki3
    otelcol-charm -->|Loki Push API| loki2
```

### Why you need an OpenTelemetry Collector

What should logs look like before reaching Loki?

In order to label logs consistently and make reliable dashboards, we need the OWASP information to be a nested **attribute**. Here's what a log line looks like in OTel format:

```json
{
    "body": "Administrator banana-bob has updated privileges of user coconut-charlie from user to admin",
    "severity_number": 13,
    "severity_text": "WARN",
    "attributes": {
        "owasp_event": {
            "datetime": "2025-09-19T14:31:58.140099+02:00",
            "type": "security",
            "appid": "example.appid",
            "event": "authz_admin:coconut-charlie,user_privilege_change",
            "level": "WARNING",
            "description": "Administrator banana-bob has updated privileges of user coconut-charlie from user to admin"
        },
        "code.file.path": "/home/aegis/Repositories/Canonical/owasp-logger/src/owasp_logger/logger.py",
        "code.function.name": "_log_event",
        "code.line.number": 26
    },
    "dropped_attributes": 0,
    "timestamp": "2025-09-19T12:31:58.140189Z",
    "observed_timestamp": "2025-09-19T12:31:58.140207Z",
    "trace_id": "0x00000000000000000000000000000000",
    "span_id": "0x0000000000000000",
    "trace_flags": 0,
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.33.1",
            "service.name": "example-service"
        },
        "schema_url": ""
    }
}
```

The `owasp_event` attribute will be mapped as-is to **structured metadata** in Loki. The metadata existing with this format is foundational to any dashboard trying to visualize OWASP information.

Given that logs can have various formats depending on the application, the easiest way to get those attributes in place is to configure some *custom processors* in an OpenTelemetry Collector to parse the OWASP information from your log line. The following sections explain how to do so.

### How to configure an OpenTelemetry Collector

#### Logs following OTel format

If the application is already using the OTel format for logs, `OWASPLogger` will make sure the OWASP information is in the correct place, so there are no additional steps.

#### Logs having arbitray format

You have to add some custom processors to the OpenTelemetry Collector configuration to parse the OWASP json blob from your logs.

> [info]- How do I configure custom processors?
> In the **charm**, use the `custom_processors` Juju config option.
> In the **snap**, add the processors config under the `processors:` top-level key, then add the processor name in the related logs pipeline.


