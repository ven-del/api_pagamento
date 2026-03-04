"""
Serviço de tratamento de webhooks do Pagar.me.

Mantém um log em memória dos últimos eventos recebidos (sem banco de dados).
"""
import logging
from collections import deque
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Log em memória — armazena os últimos MAX_LOGS eventos recebidos
MAX_LOGS = 100
_webhook_logs: deque = deque(maxlen=MAX_LOGS)

# Descrições amigáveis dos tipos de evento
EVENT_DESCRIPTIONS = {
    "order.paid": "Pedido pago",
    "order.payment_failed": "Falha no pagamento do pedido",
    "order.canceled": "Pedido cancelado",
    "charge.paid": "Cobrança paga",
    "charge.payment_failed": "Falha na cobrança",
    "charge.refunded": "Cobrança estornada",
    "subscription.created": "Assinatura criada",
    "subscription.updated": "Assinatura atualizada",
    "subscription.canceled": "Assinatura cancelada",
    "invoice.created": "Fatura criada",
    "invoice.paid": "Fatura paga",
    "invoice.payment_failed": "Falha no pagamento da fatura",
    "invoice.canceled": "Fatura cancelada",
    "plan.created": "Plano criado",
    "checkout.created": "Checkout criado",
    "checkout.closed": "Checkout processado/pago",
    "checkout.canceled": "Link de checkout expirado",
}


def process_webhook(payload: dict) -> dict:
    """
    Processa o payload recebido do Pagar.me, loga o evento e armazena
    em memória para consulta posterior.
    """
    event_type = payload.get("type", "unknown")
    description = EVENT_DESCRIPTIONS.get(event_type, "Evento desconhecido")

    data = payload.get("data", {})
    object_id = data.get("id", "—")
    account_id = payload.get("account", {}).get("id", "—")

    entry = {
        "received_at": datetime.now(tz=timezone.utc).isoformat(),
        "event_type": event_type,
        "description": description,
        "object_id": object_id,
        "account_id": account_id,
        "payload": payload,
    }

    _webhook_logs.appendleft(entry)

    logger.info(
        "[Webhook] %s | objeto: %s | conta: %s",
        event_type,
        object_id,
        account_id,
    )

    return entry


def get_webhook_logs() -> list:
    """Retorna a lista de eventos recebidos (mais recente primeiro)."""
    return list(_webhook_logs)


def clear_webhook_logs() -> None:
    """Limpa o log em memória (útil para testes)."""
    _webhook_logs.clear()
