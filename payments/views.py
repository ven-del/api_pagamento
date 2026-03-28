import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .services.checkout import create_checkout_link
from .services.invoices import cancel_invoice, get_invoice, list_invoices
from .services.pix import create_pix_order
from .services.plans import create_plan, delete_plan, get_plan, list_plans
from .services.subscriptions import (
    cancel_subscription,
    create_standalone_subscription,
    create_subscription_from_plan,
    get_subscription,
    list_subscriptions,
)
from .services.webhooks import get_webhook_logs, process_webhook


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

def index(request):
    return render(request, "payments/index.html")


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

def checkout_create(request):
    """
    GET  → Exibe formulário para configurar o checkout.
    POST → Cria o link de checkout no Pagar.me e redireciona para a URL.
    """
    if request.method == "POST":
        amount_brl = request.POST.get("amount", "100.00")
        name = request.POST.get("name", "Link de Teste")
        description = request.POST.get("description", "Produto Teste")

        try:
            amount_cents = int(float(amount_brl.replace(",", ".")) * 100)
        except (ValueError, AttributeError):
            amount_cents = 10000

        try:
            data = create_checkout_link(
                amount=amount_cents,
                name=name,
                description=description,
            )
            payment_url = data.get("payment_url") or data.get("url", "")
            if payment_url:
                return redirect(payment_url)
            return render(request, "payments/checkout.html", {
                "error": "Link criado, mas URL de pagamento não encontrada.",
                "raw": data,
            })
        except ValueError as exc:
            return render(request, "payments/checkout.html", {"error": str(exc)})

    return render(request, "payments/checkout.html")


# ---------------------------------------------------------------------------
# PIX
# ---------------------------------------------------------------------------

def pix_create(request):
    """
    GET  → Exibe formulário para criar pedido PIX.
    POST → Cria pedido PIX no Pagar.me e exibe o QR code.
    """
    if request.method == "POST":
        amount_brl = request.POST.get("amount", "10.00")
        customer_name = request.POST.get("customer_name", "Usuário Teste")
        customer_email = request.POST.get(
            "customer_email", "usuarioteste@labce.com.br")
        customer_document = request.POST.get(
            "customer_document", "00000000000")
        expires_in = int(request.POST.get("expires_in", 3600))

        try:
            amount_cents = int(float(amount_brl.replace(",", ".")) * 100)
        except (ValueError, AttributeError):
            amount_cents = 1000

        try:
            result = create_pix_order(
                amount=amount_cents,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_document=customer_document,
                expires_in=expires_in,
            )
            result["amount_cents_debug"] = amount_cents
            result["amount_brl_debug"] = amount_brl
            return render(request, "payments/pix.html", {"result": result})
        except ValueError as exc:
            error_str = str(exc)
            error_details = None
            # Tenta extrair JSON da resposta da API
            try:
                if "[" in error_str and "]" in error_str:
                    # Tenta encontrar JSON dentro da mensagem de erro
                    start = error_str.find("{")
                    if start != -1:
                        end = error_str.rfind("}") + 1
                        json_str = error_str[start:end]
                        error_details = json.dumps(json.loads(json_str), indent=2)
            except (json.JSONDecodeError, ValueError):
                pass
            
            return render(request, "payments/pix.html", {
                "error": error_str,
                "error_details": error_details,
                "debug_amount_cents": amount_cents,
                "debug_amount_brl": amount_brl,
            })

    return render(request, "payments/pix.html")


# ---------------------------------------------------------------------------
# Planos
# ---------------------------------------------------------------------------

def plan_list(request):
    """Lista todos os planos cadastrados no Pagar.me."""
    try:
        data = list_plans()
        plans = data.get("data", [])
        error = None
    except ValueError as exc:
        plans = []
        error = str(exc)
    return render(request, "payments/plan_list.html", {"plans": plans, "error": error})


def plan_create(request):
    """
    GET  → Exibe formulário para criar um plano.
    POST → Cria o plano no Pagar.me e redireciona para o detalhe.
    """
    if request.method == "POST":
        name = request.POST.get("name", "Plano Básico")
        description = request.POST.get("description", "Plano mensal básico")
        interval = request.POST.get("interval", "month")
        interval_count = int(request.POST.get("interval_count", 1))
        billing_type = request.POST.get("billing_type", "prepaid")
        item_name = request.POST.get("item_name", "Assinatura")
        price_brl = request.POST.get("price", "29.90")

        try:
            price_cents = int(float(price_brl.replace(",", ".")) * 100)
        except (ValueError, AttributeError):
            price_cents = 2990

        items = [{
            "name": item_name,
            "quantity": 1,
            "pricing_scheme": {"price": price_cents},
        }]

        try:
            plan = create_plan(
                name=name,
                description=description,
                interval=interval,
                interval_count=interval_count,
                items=items,
                billing_type=billing_type,
            )
            return redirect("plan_detail", plan_id=plan["id"])
        except ValueError as exc:
            return render(request, "payments/plan_create.html", {"error": str(exc)})

    return render(request, "payments/plan_create.html")


def plan_detail(request, plan_id):
    """Exibe os detalhes de um plano específico."""
    try:
        plan = get_plan(plan_id)
        error = None
    except ValueError as exc:
        plan = None
        error = str(exc)
    return render(request, "payments/plan_detail.html", {"plan": plan, "error": error})


def plan_delete(request, plan_id):
    """POST → Exclui o plano e redireciona para a lista."""
    if request.method == "POST":
        try:
            delete_plan(plan_id)
            return redirect("plan_list")
        except ValueError as exc:
            try:
                plan = get_plan(plan_id)
            except ValueError:
                plan = {"id": plan_id}
            return render(request, "payments/plan_detail.html", {
                "plan": plan,
                "error": str(exc),
            })
    return redirect("plan_detail", plan_id=plan_id)


# ---------------------------------------------------------------------------
# Assinaturas
# ---------------------------------------------------------------------------

def subscription_list(request):
    """Lista todas as assinaturas cadastradas no Pagar.me."""
    try:
        data = list_subscriptions()
        subscriptions = data.get("data", [])
        error = None
    except ValueError as exc:
        subscriptions = []
        error = str(exc)
    return render(request, "payments/subscription_list.html", {
        "subscriptions": subscriptions,
        "error": error,
    })


def subscription_create(request):
    """
    GET  → Exibe formulário para criar assinatura (de plano ou avulsa).
    POST → Cria a assinatura no Pagar.me e redireciona para o detalhe.
    """
    try:
        plans_data = list_plans()
        plans = [p for p in plans_data.get(
            "data", []) if p.get("status") == "active"]
    except ValueError:
        plans = []

    if request.method == "POST":
        mode = request.POST.get("mode", "plan")

        customer_name = request.POST.get("customer_name", "Usuário Teste")
        customer_email = request.POST.get(
            "customer_email", "usuarioteste@labce.com.br")
        customer_document = request.POST.get(
            "customer_document", "00000000000")
        card_number = request.POST.get("card_number", "4000000000000010")
        card_holder = request.POST.get("card_holder", "Usuário Teste")
        card_exp_month = int(request.POST.get("card_exp_month", 12))
        card_exp_year = int(request.POST.get("card_exp_year", 2030))
        card_cvv = request.POST.get("card_cvv", "123")

        try:
            if mode == "plan":
                plan_id = request.POST.get("plan_id", "")
                sub = create_subscription_from_plan(
                    plan_id=plan_id,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_document=customer_document,
                    card_number=card_number,
                    card_holder_name=card_holder,
                    card_exp_month=card_exp_month,
                    card_exp_year=card_exp_year,
                    card_cvv=card_cvv,
                )
            else:
                price_brl = request.POST.get("price", "29.90")
                try:
                    price_cents = int(float(price_brl.replace(",", ".")) * 100)
                except (ValueError, AttributeError):
                    price_cents = 2990

                sub = create_standalone_subscription(
                    item_description=request.POST.get(
                        "item_description", "Assinatura mensal"),
                    item_price=price_cents,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_document=customer_document,
                    interval=request.POST.get("interval", "month"),
                    interval_count=int(request.POST.get("interval_count", 1)),
                    billing_type=request.POST.get("billing_type", "prepaid"),
                    card_number=card_number,
                    card_holder_name=card_holder,
                    card_exp_month=card_exp_month,
                    card_exp_year=card_exp_year,
                    card_cvv=card_cvv,
                )

            return redirect("subscription_detail", sub_id=sub["id"])
        except ValueError as exc:
            return render(request, "payments/subscription_create.html", {
                "error": str(exc),
                "plans": plans,
            })

    return render(request, "payments/subscription_create.html", {"plans": plans})


def subscription_detail(request, sub_id):
    """Exibe os detalhes de uma assinatura específica."""
    try:
        sub = get_subscription(sub_id)
        error = None
    except ValueError as exc:
        sub = None
        error = str(exc)
    return render(request, "payments/subscription_detail.html", {
        "sub": sub,
        "error": error,
    })


def subscription_cancel(request, sub_id):
    """POST → Cancela a assinatura e redireciona para a lista."""
    if request.method == "POST":
        try:
            cancel_subscription(sub_id)
            return redirect("subscription_list")
        except ValueError as exc:
            try:
                sub = get_subscription(sub_id)
            except ValueError:
                sub = {"id": sub_id}
            return render(request, "payments/subscription_detail.html", {
                "sub": sub,
                "error": str(exc),
            })
    return redirect("subscription_detail", sub_id=sub_id)


# ---------------------------------------------------------------------------
# Faturas
# ---------------------------------------------------------------------------

def invoice_list(request, sub_id):
    """Lista todas as faturas de uma assinatura."""
    try:
        sub = get_subscription(sub_id)
        error_sub = None
    except ValueError as exc:
        sub = {"id": sub_id}
        error_sub = str(exc)

    try:
        data = list_invoices(sub_id)
        invoices = data.get("data", [])
        for inv in invoices:
            inv["amount_brl"] = inv.get("amount", 0) / 100
        error = None
    except ValueError as exc:
        invoices = []
        error = str(exc)

    return render(request, "payments/invoice_list.html", {
        "sub": sub,
        "invoices": invoices,
        "error": error or error_sub,
    })


def invoice_detail(request, invoice_id):
    """Exibe os detalhes de uma fatura específica."""
    try:
        invoice = get_invoice(invoice_id)
        if invoice:
            invoice["amount_brl"] = invoice.get("amount", 0) / 100
        error = None
    except ValueError as exc:
        invoice = None
        error = str(exc)
    return render(request, "payments/invoice_detail.html", {
        "invoice": invoice,
        "error": error,
    })


def invoice_cancel(request, invoice_id):
    """POST → Cancela a fatura e redireciona para o detalhe."""
    if request.method == "POST":
        try:
            cancel_invoice(invoice_id)
            return redirect("invoice_detail", invoice_id=invoice_id)
        except ValueError as exc:
            try:
                invoice = get_invoice(invoice_id)
            except ValueError:
                invoice = {"id": invoice_id}
            return render(request, "payments/invoice_detail.html", {
                "invoice": invoice,
                "error": str(exc),
            })
    return redirect("invoice_detail", invoice_id=invoice_id)


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------

@csrf_exempt
def webhook_receiver(request):
    """
    Endpoint POST que recebe eventos do Pagar.me.
    Retorna HTTP 200 para confirmar recebimento.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        payload = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Payload inválido"}, status=400)

    process_webhook(payload)
    return JsonResponse({"status": "ok"}, status=200)


def webhook_log(request):
    """Exibe os últimos eventos de webhook recebidos (armazenados em memória)."""
    logs = get_webhook_logs()
    return render(request, "payments/webhook_log.html", {"logs": logs})
