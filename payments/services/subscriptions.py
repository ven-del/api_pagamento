"""
Serviço de Assinaturas de Recorrência do Pagar.me.

Endpoints:
  POST   /subscriptions
  GET    /subscriptions
  GET    /subscriptions/{id}
  DELETE /subscriptions/{id}
  PATCH  /subscriptions/{id}/card
  PATCH  /subscriptions/{id}/payment-method
"""
from .base import PagarmeClient


def _build_customer(
    name: str,
    email: str,
    document: str,
) -> dict:
    return {
        "name": name,
        "email": email,
        "type": "individual",
        "document": document,
        "phones": {
            "mobile_phone": {
                "country_code": "55",
                "area_code": "11",
                "number": "999999999",
            }
        },
    }


def _build_card(
    number: str,
    holder_name: str,
    exp_month: int,
    exp_year: int,
    cvv: str,
) -> dict:
    return {
        "number": number,
        "holder_name": holder_name,
        "exp_month": exp_month,
        "exp_year": exp_year,
        "cvv": cvv,
    }


def create_subscription_from_plan(
    plan_id: str,
    customer_name: str,
    customer_email: str,
    customer_document: str,
    card_number: str = "4000000000000010",
    card_holder_name: str = "Usuário Teste",
    card_exp_month: int = 12,
    card_exp_year: int = 2030,
    card_cvv: str = "123",
) -> dict:
    """Cria uma assinatura vinculada a um plano existente."""
    client = PagarmeClient()
    payload = {
        "plan_id": plan_id,
        "payment_method": "credit_card",
        "customer": _build_customer(customer_name, customer_email, customer_document),
        "card": _build_card(
            card_number, card_holder_name, card_exp_month, card_exp_year, card_cvv
        ),
    }
    return client.post("/subscriptions", payload)


def create_standalone_subscription(
    item_description: str,
    item_price: int,
    customer_name: str,
    customer_email: str,
    customer_document: str,
    interval: str = "month",
    interval_count: int = 1,
    billing_type: str = "prepaid",
    card_number: str = "4000000000000010",
    card_holder_name: str = "Usuário Teste",
    card_exp_month: int = 12,
    card_exp_year: int = 2030,
    card_cvv: str = "123",
) -> dict:
    """Cria uma assinatura avulsa (sem plano pré-existente)."""
    client = PagarmeClient()
    payload = {
        "payment_method": "credit_card",
        "interval": interval,
        "interval_count": interval_count,
        "billing_type": billing_type,
        "installments": 1,
        "customer": _build_customer(customer_name, customer_email, customer_document),
        "card": _build_card(
            card_number, card_holder_name, card_exp_month, card_exp_year, card_cvv
        ),
        "items": [
            {
                "description": item_description,
                "quantity": 1,
                "pricing_scheme": {"price": item_price},
            }
        ],
    }
    return client.post("/subscriptions", payload)


def list_subscriptions() -> dict:
    """Lista todas as assinaturas."""
    client = PagarmeClient()
    return client.get("/subscriptions")


def get_subscription(subscription_id: str) -> dict:
    """Obtém os detalhes de uma assinatura específica."""
    client = PagarmeClient()
    return client.get(f"/subscriptions/{subscription_id}")


def cancel_subscription(subscription_id: str) -> dict:
    """Cancela uma assinatura."""
    client = PagarmeClient()
    return client.delete(f"/subscriptions/{subscription_id}")
