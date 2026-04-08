import urllib.request
import urllib.error
import json
from typing import Any

class HttpSession:
    """Simple HTTP session wrapper using stdlib only."""

    def __init__(self, base_url: str = "", headers: dict | None = None, timeout: int = 30):
        self._base_url = base_url
        self._headers = headers or {"Content-Type": "application/json"}
        self._timeout = timeout

    def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        url = self._base_url + path
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)
        req = urllib.request.Request(url, headers=self._headers)
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.URLError as e:
            raise ConnectionError(f"HTTP GET {url} failed: {e}") from e

    def post(self, path: str, body: dict | None = None) -> dict[str, Any]:
        url = self._base_url + path
        data = json.dumps(body or {}).encode()
        req = urllib.request.Request(url, data=data, headers=self._headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.URLError as e:
            raise ConnectionError(f"HTTP POST {url} failed: {e}") from e
