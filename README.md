# OWASP Logger

**🚧 This readme is work in progress! 🚧**

## Installation

The package is not yet in PyPi, so you should install it from the git repo:

```bash
# Standalone logger (without OTel dependencies)
uv pip install "git+https://github.com/lucabello/owasp-logger"
# Additional OTel logger
uv pip install "git+https://github.com/lucabello/owasp-logger[otel]"
```

## Usage

Example usage:

```
# Create a virtual environment
uv venv  # or the classic 'python -m venv .venv'
source .venv/bin/activate

# Install the owasp-logger library
uv pip install "git+https://github.com/lucabello/owasp-logger"

# Try the logger from the Python shell
python
>>> from owasp_logger import OWASPLogger
>>> logger = OWASPLogger(appid="coconut.app")
>>> logger.authn_login_lock(user="banana-bob")
{"datetime": "2025-09-26T12:37:37.886421+02:00", "appid": "coconut.app", "event": "authn_login_lock:banana-bob,maxretries", "level": "WARNING", "description": "User banana-bob login locked because maxretries exceeded", "type": "security"}

# Try out the examples
python examples/nested_json.py

# If you want the OTel format, install the owasp-logger[otel] extension
uv pip install "git+https://github.com/lucabello/owasp-logger[otel]"
python examples/otel.py
```

## Assumptions

TODO: Restructure this

- Python 3.11 for Unpack (reimplement it in the library from typing_extensions?)
- All the logs flow through OTLP relations (no deprecated Loki exporter)
- Loki 3
- For charm developers, you *must* have an otelcol (no direct writes to Loki) or you don't get the correct attributes

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
    app --> otlplog["otlp.log"]
    otlplog --> otelcol-snap
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

This README classifies logs according to the [OpenTelemetry documentation](https://opentelemetry.io/docs/concepts/signals/logs/).

Note that all configuration snippets are not *complete configuration files*, but only show the relevant sections for the sake of simplicity.

#### Structured logs

A structured log is a log whose textual format follows a consistent, machine-readable format. For applications, one of the most common formats is JSON.

##### OpenTelemetry format

If the application is already using the OTel format for logs, `OWASPLogger` will make sure the OWASP information is in the correct place. Assuming you have a dedicated file for these JSON logs, you can use the `filelog` receiver to parse them:

```yaml
receivers:
  filelog:
    include:
      - /path/to/your/file.log

processors:
  # Parse the OTel format from the JSON log lines in the file
  transform/parse-json:
    log_statements:
      - context: log
        error_mode: ignore  # Log the error and continue (ignore|silent|propagate)
        statements:
          - merge_maps(log.cache, ParseJSON(log.body), "upsert") where IsMatch(log.body, "^\\{")
          - set(log.body, log.cache["body"])
          - set(log.severity_number, Int(log.cache["severity_number"]))
          - set(log.severity_text, log.cache["severity_text"])
          - merge_maps(log.attributes, log.cache["attributes"], "upsert")
          - set(log.dropped_attributes_count, Int(log.cache["dropped_attributes"]))
          - set(log.time, Time(log.cache["timestamp"], "%FT%T.%fZ"))
          - set(log.trace_id, log.cache["trace_id"])
          - set(log.span_id, log.cache["span_id"])
          - merge_maps(resource.attributes, log.cache["resource"]["attributes"], "upsert")

service:
  pipelines:
    logs:
      receivers: [filelog]
      processors: [transform/parse-json]
```

More information on the OTel log data model can be found here:
- [OpenTelemetry: Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [OpenTelemetry: Internal Log Context (representation)](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/pkg/ottl/contexts/ottllog)


##### Generic JSON

If you have generic, arbitrarily-nested JSON logs in a file, you'll have to configure the transform processor accordingly in order to parse the relevant information.

```yaml
transform/parse-json:
  log_statements:
    - context: log
      statements:
        - merge_maps(log.cache, ParseJSON(log.body), "upsert") where IsMatch(log.body, "^\\{")
        - # parse the relevant fields as needed
```


#### Semistructured Logs

A semistructured log is a log that does use some self-consistent patterns to distinguish data so that it’s machine-readable, but may not use the same formatting and delimiters between data across different systems. One example of this is `juju debug-log`.

You have to add some custom processors to the OpenTelemetry Collector configuration to parse the OWASP json blob from your logs.

> [!NOTE]
> **How do I configure custom processors?**  
> In the **charm**, use the `custom_processors` Juju config option.
> In the **snap**, add the processors config under the `processors:` top-level key, then add the processor name in the related logs pipeline.

##### juju debug-log

`juju debug-log` embeds the OWASP event blob as a JSON in their own logs. Parsing its values into attributes is simple:

```yaml
transform/parse-juju:
  log_statements:
    - context: log
      error_mode: ignore  # switch to ignore
      statements:
        - merge_maps(log.cache, ExtractPatterns(body, "^(?P<prefix>.*?)(?P<json>\\{.*\\}?)$"), "upsert")
        - merge_maps(log.attributes, ParseJSON(log.cache["json"]), "upsert")
```



#### Unstructured logs

Unstructured logs don't follow a consistent structure, and are thus more difficult to parse and analyze at scale. You need to **write your own custom parsing logic** in some processor in order to extract the *attributes* and fields you need.

## Visualizing OWASP Logs in Grafana

TODO: write this section

TODO: add how logs appear in Loki (structured metadata?) and how to make a dashboard from them
