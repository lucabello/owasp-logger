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
