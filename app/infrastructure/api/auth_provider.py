from app.infrastructure.secrets.secrets_provider import SecretsProvider

class AuthProvider:
    def __init__(self, secrets: SecretsProvider):
        self._secrets = secrets

    def get_polymarket_headers(self) -> dict:
        api_key = self._secrets.get_polymarket_api_key()
        if api_key:
            return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def get_binance_headers(self) -> dict:
        api_key = self._secrets.get_binance_api_key()
        if api_key:
            return {"X-MBX-APIKEY": api_key, "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}
