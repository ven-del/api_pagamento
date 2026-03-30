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
    name: str = "Plano Básico",
    interval: str = "month",
    interval_count: int = 1,
    scheme_type: str = "Unit",
    price: int = 2990,
    quantity: int = 1,
) -> dict:
    """Cria um plano de recorrência com os campos exigidos pela API."""
    client = PagarmeClient()
    payload = {
        "name": name,
        "interval": interval,
        "interval_count": interval_count,
        "pricing_scheme": {
            "scheme_type": scheme_type,
            "price": price,
        },
        "quantity": quantity,
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
