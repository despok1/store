# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html

# Worker timeout in seconds.
# Increased from the default 30s to 120s to prevent SIGKILL on slow requests
# while slow database queries and API calls are being investigated and optimised.
timeout = 120
