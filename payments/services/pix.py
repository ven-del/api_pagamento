"""
Serviço de pagamento via PIX do Pagar.me.

Endpoint: POST /orders
"""
from .base import PagarmeClient


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
    - Valor <= 50000 centavos (R$ 500,00) → sucesso (pending → paid automático)
    - Valor >  50000 centavos             → falha

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

    data = client.post("/orders", payload)

    # Extrai QR code da resposta para facilitar exibição no template
    try:
        last_tx = data["charges"][0]["last_transaction"]
        data["qr_code"] = last_tx.get("qr_code", "")
        data["qr_code_url"] = last_tx.get("qr_code_url", "")
    except (KeyError, IndexError, TypeError):
        data["qr_code"] = ""
        data["qr_code_url"] = ""

    return data
