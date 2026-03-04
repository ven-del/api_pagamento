"""
Serviço de Faturas (Invoices) do Pagar.me.

Endpoints:
  GET    /subscriptions/{subscription_id}/invoices
  GET    /invoices/{invoice_id}
  DELETE /invoices/{invoice_id}
"""
from .base import PagarmeClient


def list_invoices(subscription_id: str) -> dict:
    """Lista todas as faturas de uma assinatura."""
    client = PagarmeClient()
    return client.get(f"/subscriptions/{subscription_id}/invoices")


def get_invoice(invoice_id: str) -> dict:
    """Obtém os detalhes de uma fatura específica."""
    client = PagarmeClient()
    return client.get(f"/invoices/{invoice_id}")


def cancel_invoice(invoice_id: str) -> dict:
    """Cancela uma fatura. Ação irreversível."""
    client = PagarmeClient()
    return client.delete(f"/invoices/{invoice_id}")
