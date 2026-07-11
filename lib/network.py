from lib.colors import bcolors as c
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 15

class TimeoutHTTPAdapter(HTTPAdapter):
  """
  HTTPAdapter variant that enforces a default request timeout when the
  caller does not specify one. Without this, a dead connection can hang
  forever instead of raising a retryable network error.
  """

  def __init__(self, *args, timeout=DEFAULT_TIMEOUT, **kwargs):
    self.timeout = timeout
    super().__init__(*args, **kwargs)

  def send(self, request, **kwargs):
    if kwargs.get("timeout") is None:
      kwargs["timeout"] = self.timeout
    return super().send(request, **kwargs)

class LoggingRetry(Retry):
  """
  Retry variant that prints a reconnect message before each retry attempt,
  so silent multi-second waits (backoff) do not look like a frozen script.
  """

  def increment(self, *args, **kwargs):
    new_retry = super().increment(*args, **kwargs)
    attempt = self.total if self.total is not None else 0
    print(f"{c.FG_YELLOW}[!] Connection issue detected. Reconnecting... ({new_retry.total} retries left){c.END}")
    return new_retry

def attachRetry(session, total=5, backoff_factor=2):
  """
  Mounts a retrying, timeout-enforcing adapter onto session so transient
  network errors (dropped connection, reset, refused, DNS hiccup, 5xx)
  are retried with exponential backoff before they ever reach application
  code. Only after retries are exhausted does NETWORK_ERROR bubble up.
  `session`: Session object to configure
  `total`: max retry attempts per request
  `backoff_factor`: delay multiplier between retries (seconds), e.g.
    with backoff_factor=2 delays are roughly 2s, 4s, 8s, 16s, 32s
  """
  retry = LoggingRetry(
    total=total,
    connect=total,
    read=total,
    status=total,
    backoff_factor=backoff_factor,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
    raise_on_status=False,
  )
  adapter = TimeoutHTTPAdapter(max_retries=retry)
  session.mount("https://", adapter)
  session.mount("http://", adapter)
  return session
