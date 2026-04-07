import requests

NETWORK_ERRORS = (
    ConnectionError,
    ConnectionAbortedError,
    ConnectionRefusedError,
    ConnectionResetError,
    requests.exceptions.RequestException,
)
