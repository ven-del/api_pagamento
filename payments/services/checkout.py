"""
Serviço de Checkout (Link de Pagamento) do Pagar.me.

Endpoint: POST /paymentlinks
"""
from django.conf import settings

from .base import PagarmeClient


def create_checkout_link(
    amount: int,
    name: str = "Link de Teste",
    description: str = "Produto Teste",
    payment_methods: list[str] | None = None,
) -> dict:
    """
    Cria um link de checkout hospedado no Pagar.me.

    Args:
        amount:          Valor total em centavos.
        name:            Nome do pedido exibido no checkout.
        description:     Descrição do item.
        payment_methods: Lista de métodos aceitos. Padrão: cartão, pix, boleto.

    Returns:
        Dicionário com a resposta da API (inclui ``payment_url``).
    """
    if payment_methods is None:
        payment_methods = ["credit_card"]

    payment_methods = [method for method in payment_methods if method == "credit_card"]
    if not payment_methods:
        payment_methods = ["credit_card"]

    client = PagarmeClient()
    # Para Create Link em ambiente de teste, a documentação oficial orienta
    # usar o host sdx-api com chave sk_test.
    secret_key = str(getattr(settings, "PAGARME_SECRET_KEY", "")).strip()
    if secret_key.startswith("sk_test_"):
        client.BASE_URL = "https://sdx-api.pagar.me/core/v5"

    payload = {
        "is_building": False,
        "name": name,
        "type": "order",
        "payment_settings": {
            "accepted_payment_methods": payment_methods,
            "credit_card_settings": {
                "installments_setup": {
                    "amount": amount,
                    "interest_rate": 0,
                    "max_installments": 1,
                    "interest_type": "simple",
                },
                "operation_type": "auth_and_capture",
            },
        },
        "cart_settings": {
            "items": [
                {
                    "amount": amount,
                    "name": description,
                    "default_quantity": 1,
                }
            ]
        },
    }
    return client.post("/paymentlinks", payload)
