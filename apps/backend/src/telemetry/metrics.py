from prometheus_client import Counter, Histogram, Gauge

# Application Wide Metrics

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["method", "endpoint"]
)

# Background Task Metrics
agent_run_total = Counter(
    "agent_run_total",
    "Total number of Agent Runs (Pipelines) executed",
    ["run_type", "status"]
)

agent_run_duration_seconds = Histogram(
    "agent_run_duration_seconds",
    "Duration of Agent Runs in seconds",
    ["run_type"]
)

# Active Connections Gauge
active_users = Gauge(
    "active_users_logged_in",
    "Approximate number of logged in user sessions currently active"
)
