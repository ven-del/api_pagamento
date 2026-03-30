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
    billing_address: dict | None = None,
) -> dict:
    card = {
        "number": number,
        "holder_name": holder_name,
        "exp_month": exp_month,
        "exp_year": exp_year,
        "cvv": cvv,
    }
    if billing_address:
        card["billing_address"] = billing_address
    return card


def create_subscription_from_plan(
    plan_id: str,
    customer_name: str,
    customer_email: str,
    customer_document: str,
    card_number: str = "4000000000000010",
    card_holder_name: str = "Usuário Teste",
    card_exp_month: int = 12,
    card_exp_year: int = 2030,
    card_cvv: str = "903",
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
    customer_document: str = "",
    interval: str = "month",
    interval_count: int = 3,
    billing_type: str = "prepaid",
    installments: int = 3,
    minimum_price: int = 10000,
    boleto_due_days: int = 5,
    card_number: str = "4000000000000010",
    card_holder_name: str = "Usuário Teste",
    card_exp_month: int = 1,
    card_exp_year: int = 30,
    card_cvv: str = "123",
    card_billing_address_line_1: str = "4, Privet Drive",
    card_billing_address_line_2: str = "Bedroom under the stairs",
    card_billing_address_zip_code: str = "20021130",
    card_billing_address_city: str = "Little Whinging",
    card_billing_address_state: str = "Surrey",
    card_billing_address_country: str = "UK",
    discount_cycles: int = 3,
    discount_value: int = 10,
    discount_type: str = "percentage",
    increment_cycles: int = 2,
    increment_value: int = 20,
    increment_type: str = "percentage",
    item_quantity: int = 1,
    item_scheme_type: str = "Unit",
    setup_item_description: str = "Matrícula",
    setup_item_price: int = 5990,
    setup_item_quantity: int = 1,
    setup_item_cycles: int = 1,
    setup_item_scheme_type: str = "Unit",
    metadata_id: str = "my_subscription_id",
    quantity: int | None = None,
) -> dict:
    """Cria uma assinatura avulsa (sem plano pré-existente)."""
    client = PagarmeClient()
    customer = {
        "name": customer_name,
        "email": customer_email,
    }
    if customer_document:
        customer.update({
            "type": "individual",
            "document": customer_document,
        })

    payload = {
        "payment_method": "credit_card",
        "currency": "BRL",
        "interval": interval,
        "interval_count": interval_count,
        "billing_type": billing_type,
        "installments": installments,
        "minimum_price": minimum_price,
        "boleto_due_days": boleto_due_days,
        "customer": customer,
        "card": _build_card(
            card_number,
            card_holder_name,
            card_exp_month,
            card_exp_year,
            card_cvv,
            {
                "line_1": card_billing_address_line_1,
                "line_2": card_billing_address_line_2,
                "zip_code": card_billing_address_zip_code,
                "city": card_billing_address_city,
                "state": card_billing_address_state,
                "country": card_billing_address_country,
            },
        ),
        "discounts": [
            {
                "cycles": discount_cycles,
                "value": discount_value,
                "discount_type": discount_type,
            }
        ],
        "increments": [
            {
                "cycles": increment_cycles,
                "value": increment_value,
                "discount_type": increment_type,
            }
        ],
        "items": [
            {
                "description": item_description,
                "quantity": item_quantity,
                "pricing_scheme": {
                    "price": item_price,
                    "scheme_type": item_scheme_type,
                },
            },
            {
                "description": setup_item_description,
                "quantity": setup_item_quantity,
                "cycles": setup_item_cycles,
                "pricing_scheme": {
                    "price": setup_item_price,
                    "scheme_type": setup_item_scheme_type,
                },
            }
        ],
        "metadata": {"id": metadata_id},
        "pricing_scheme": {"scheme_type": "Unit"},
        "quantity": quantity,
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
