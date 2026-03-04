"""
Serviço de Planos de Recorrência do Pagar.me.

Endpoints:
  POST   /plans
  GET    /plans
  GET    /plans/{plan_id}
  PUT    /plans/{plan_id}
  DELETE /plans/{plan_id}
"""
from .base import PagarmeClient


def create_plan(
    name: str,
    description: str = "",
    interval: str = "month",
    interval_count: int = 1,
    billing_type: str = "prepaid",
    items: list | None = None,
    payment_methods: list[str] | None = None,
    installments: list[int] | None = None,
) -> dict:
    """Cria um plano de recorrência."""
    if payment_methods is None:
        payment_methods = ["credit_card"]
    if installments is None:
        installments = [1]
    if items is None:
        items = [
            {
                "name": name,
                "quantity": 1,
                "pricing_scheme": {"price": 2990},
            }
        ]

    client = PagarmeClient()
    payload = {
        "name": name,
        "description": description,
        "interval": interval,
        "interval_count": interval_count,
        "billing_type": billing_type,
        "payment_methods": payment_methods,
        "installments": installments,
        "items": items,
    }
    return client.post("/plans", payload)


def list_plans() -> dict:
    """Lista todos os planos cadastrados."""
    client = PagarmeClient()
    return client.get("/plans")


def get_plan(plan_id: str) -> dict:
    """Obtém os detalhes de um plano específico."""
    client = PagarmeClient()
    return client.get(f"/plans/{plan_id}")


def delete_plan(plan_id: str) -> dict:
    """Exclui um plano. Retorna a resposta da API."""
    client = PagarmeClient()
    return client.delete(f"/plans/{plan_id}")
