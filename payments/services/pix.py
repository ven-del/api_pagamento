"""
Serviço de pagamento via PIX do Pagar.me.

Endpoint: POST /orders
"""
import json
import logging
from .base import PagarmeClient

logger = logging.getLogger(__name__)


def _extract_pix_qr_code(data: dict) -> tuple[str, str]:
    """Extrai o QR Code e a URL do QR Code de diferentes formatos de resposta."""
    candidates = []

    charges = data.get("charges") if isinstance(data, dict) else None
    if isinstance(charges, list) and charges:
        first_charge = charges[0]
        if isinstance(first_charge, dict):
            last_transaction = first_charge.get("last_transaction")
            if isinstance(last_transaction, dict):
                candidates.append(last_transaction)

    if isinstance(data, dict):
        candidates.append(data)

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue

        qr_code = candidate.get("qr_code")
        qr_code_url = candidate.get("qr_code_url")
        if qr_code or qr_code_url:
            return qr_code or "", qr_code_url or ""

    return "", ""


def create_pix_order(
    amount: int,
    customer_name: str = "Usuário Teste",
    customer_email: str = "usuarioteste@labce.com.br",
    customer_document: str = "00000000000",
    expires_in: int = 3600,
) -> dict:
    """
    Cria um pedido com pagamento via PIX.

    Regras do simulador:
    - Valor < 50000 centavos (R$ 500,00) → sucesso (pending → paid automático)
    - Valor >= 50000 centavos            → falha

    Returns:
        Dicionário enriquecido com ``qr_code`` e ``qr_code_url``.
    """
    client = PagarmeClient()
    payload = {
        "items": [
            {
                "amount": amount,
                "description": "Pagamento via PIX",
                "quantity": 1,
            }
        ],
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "type": "individual",
            "document": customer_document,
            "phones": {
                "mobile_phone": {
                    "country_code": "55",
                    "area_code": "11",
                    "number": "999999999",
                }
            },
        },
        "payments": [
            {
                "payment_method": "pix",
                "pix": {
                    "expires_in": expires_in,
                },
            }
        ],
    }

    logger.info(f"[PIX] Enviando payload: {json.dumps(payload, indent=2)}")

    try:
        data = client.post("/orders", payload)
        logger.info(
            f"[PIX] Sucesso na requisição. Resposta: {json.dumps(data, indent=2)}")
    except ValueError as e:
        logger.error(f"[PIX] Erro ao criar pedido: {str(e)}")
        raise

    # Extrai QR code da resposta para facilitar exibição no template
    qr_code, qr_code_url = _extract_pix_qr_code(data)
    data["qr_code"] = qr_code
    data["qr_code_url"] = qr_code_url

    return data
