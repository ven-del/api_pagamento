"""
Serviço de Checkout (Link de Pagamento) do Pagar.me.

Endpoint: POST /checkout/links
"""
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
        payment_methods = ["credit_card", "pix", "boleto"]

    client = PagarmeClient()
    payload = {
        "name": name,
        "type": "order",
        "payment_settings": {
            "accepted_payment_methods": payment_methods,
            "credit_card": {
                "installments": [{"number": 1, "total": amount}],
            },
        },
        "cart_settings": {
            "items": [
                {
                    "amount": amount,
                    "description": description,
                    "quantity": 1,
                }
            ]
        },
        "customer_settings": {
            "customer_editable": True,
        },
    }
    return client.post("/checkout/links", payload)
