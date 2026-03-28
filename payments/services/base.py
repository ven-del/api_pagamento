"""
Client HTTP base para a API do Pagar.me V5.

Encapsula autenticação Basic Auth e os métodos HTTP genéricos
utilizados por todos os serviços da aplicação.
"""
import base64
import json
import requests
from django.conf import settings


class PagarmeClient:
    BASE_URL = "https://api.pagar.me/core/v5"

    def __init__(self):
        secret_key = str(getattr(settings, "PAGARME_SECRET_KEY", "")).strip()
        if not secret_key:
            raise ValueError(
                "PAGARME_SECRET_KEY não configurada. "
                "Adicione a chave no arquivo .env."
            )
        if not secret_key.startswith(("sk_test_", "sk_live_")):
            raise ValueError(
                "PAGARME_SECRET_KEY inválida. Use uma chave secreta iniciando com "
                "sk_test_ ou sk_live_."
            )
        # Basic Auth: base64(sk_test_...:)
        token = base64.b64encode(f"{secret_key}:".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.BASE_URL}/{path.lstrip('/')}"

    def _handle(self, response: requests.Response) -> dict:
        """Levanta ValueError com detalhes em caso de erro HTTP."""
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text}

        if not response.ok:
            message = data.get("message") or data.get("errors") or str(data)
            # Inclui a resposta JSON completa para debug
            full_response = json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
            raise ValueError(f"[{response.status_code}] {message}\n\nResposta completa:\n{full_response}")

        return data

    def get(self, path: str, params: dict | None = None) -> dict:
        resp = requests.get(
            self._url(path), headers=self._headers, params=params)
        return self._handle(resp)

    def post(self, path: str, payload: dict) -> dict:
        resp = requests.post(
            self._url(path), headers=self._headers, json=payload)
        return self._handle(resp)

    def patch(self, path: str, payload: dict) -> dict:
        resp = requests.patch(
            self._url(path), headers=self._headers, json=payload)
        return self._handle(resp)

    def delete(self, path: str) -> dict:
        resp = requests.delete(self._url(path), headers=self._headers)
        return self._handle(resp)
