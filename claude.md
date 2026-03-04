# Plano de Implementação — API de Pagamentos Pagar.me (Sandbox)

## Objetivo

Projeto Django minimalista para testar integração com a API do Pagar.me (V5) em ambiente sandbox.
Foco em velocidade de implementação: sem frontend elaborado, sem models complexos, apenas o essencial para validar cada fluxo de pagamento. Atualizar as checkboxes da fase correspondente ao concluir a implementação de uma fase. Sem emojis e sem o design system padrão de IA.

---

## Documentação de Referência

| Tema | Docs (Guia) | API Reference |
|---|---|---|
| Checkout | https://docs.pagar.me/docs/checkout-use | https://docs.pagar.me/reference/criar-link |
| Pix | https://docs.pagar.me/docs/pix-1 | https://docs.pagar.me/reference/pix-2 |
| Recorrência (overview) | https://docs.pagar.me/docs/overview-recorrência | — |
| Assinaturas | https://docs.pagar.me/docs/assinatura | https://docs.pagar.me/reference/assinaturas-1 |
| Planos | https://docs.pagar.me/docs/plano | https://docs.pagar.me/reference/planos-1 |
| Faturas | https://docs.pagar.me/docs/fatura | https://docs.pagar.me/reference/faturas-1 |
| Simuladores | https://docs.pagar.me/docs/o-que-é-um-simulador | — |
| Simulador PIX | https://docs.pagar.me/docs/simulador-pix | — |
| Simulador Cartão Crédito | https://docs.pagar.me/docs/simulador-de-cartão-de-crédito | — |
| Webhooks | https://docs.pagar.me/docs/webhooks | https://docs.pagar.me/reference/visão-geral-sobre-webhooks |
| Chaves de acesso | https://docs.pagar.me/docs/chaves-de-acesso | — |
| Autenticação | — | https://docs.pagar.me/reference/autenticação-2 |
| Criar pedido | — | https://docs.pagar.me/reference/criar-pedido-2 |

---

## Informações Importantes da API

### Base URL
```
https://api.pagar.me/core/v5
```

### Autenticação
- Utiliza **Basic Auth** com a chave secreta (`sk_test_...`) como username e senha vazia.
- Header: `Authorization: Basic base64(sk_test_xxx:)`

### Chaves
- **Chave Secreta (sk_test_...)**: usada server-side para criar transações, planos, assinaturas etc.
- **Chave Pública (pk_test_...)**: usada client-side apenas para encriptação.
- Ambas encontradas na Dashboard Pagar.me em modo **TESTE**.

### Regras do Simulador

**Cartão de Crédito (Gateway):**
| Número do Cartão | Cenário |
|---|---|
| `4000000000000010` | Sucesso — todas as operações funcionam |
| `4000000000000028` | Falha — transação não autorizada |
| `4000000000000036` | Processing → Sucesso (erro temporário, confirmado depois) |
| `4000000000000044` | Processing → Falha |
| `4000000000000077` | Sucesso → Processing → Sucesso (segunda operação) |
| `4000000000000093` | Sucesso → Processing → Sucesso (primeira operação mantida) |
| `4000000000000051` | Processing → Cancelado |
| `4000000000000069` | Paid → Chargedback |
| Qualquer outro | Não autorizado |

**PIX (Gateway):**
| Valor | Cenário |
|---|---|
| ≤ R$ 500,00 | Sucesso (status pending → paid automaticamente) |
| > R$ 500,00 | Falha (status failed) |

> **Obs:** Simulador PIX não funciona com Split.

---

## Arquitetura do Projeto

```
api_pagamento/
├── manage.py
├── requirements.txt
├── .env                        # Chaves secretas (PAGARME_SK, PAGARME_PK)
├── .env.example
├── .gitignore
├── config/                     # Projeto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── payments/                   # App principal
    ├── __init__.py
    ├── urls.py
    ├── views.py                # Views para cada fluxo
    ├── services/
    │   ├── __init__.py
    │   ├── base.py             # Client HTTP base (requests + auth)
    │   ├── checkout.py         # Serviço de Checkout (Link de Pagamento)
    │   ├── pix.py              # Serviço de Pedido com PIX
    │   ├── plans.py            # CRUD de Planos
    │   ├── subscriptions.py    # CRUD de Assinaturas
    │   ├── invoices.py         # Consulta/criação de Faturas
    │   └── webhooks.py         # Handler de Webhooks
    └── templates/payments/
        └── index.html          # Dashboard simples com links para cada teste
```

---

## Fases de Implementação

### FASE 1 — Setup do Projeto
- [&check;] Criar projeto Django: `django-admin startproject config .`
- [&check;] Criar app: `python manage.py startapp payments`
- [&check;] Instalar dependências: `pip install django requests python-decouple`
- [&check;] Criar `requirements.txt`
- [&check;] Configurar `.env` com `PAGARME_SECRET_KEY` e `PAGARME_PUBLIC_KEY`
- [&check;] Configurar `settings.py` (app registrado, ALLOWED_HOSTS, etc.)
- [&check;] Criar `.gitignore` (incluir `.env`, `db.sqlite3`, `__pycache__`)

### FASE 2 — Client HTTP Base (`payments/services/base.py`)
- [&check;] Classe `PagarmeClient` com:
  - `BASE_URL = "https://api.pagar.me/core/v5"`
  - Método `__init__` lendo a `PAGARME_SECRET_KEY` do `.env`
  - Autenticação via Basic Auth (`sk_test_...:` codificado em base64)
  - Métodos genéricos: `get()`, `post()`, `patch()`, `delete()`
  - Tratamento básico de erros (status code + json response)

### FASE 3 — Checkout (Link de Pagamento)
**Endpoint:** `POST /checkout/links`

- [&check;] Serviço `payments/services/checkout.py`:
  - `create_checkout_link(amount, name, payment_methods, ...)` → retorna URL do checkout
- [&check;] View `checkout_create` — cria um link de checkout e redireciona para a URL
- [&check;] Template `payments/templates/payments/checkout.html` — formulário de criação
- [&check;] Testar via browser/curl: criar link → abrir URL → pagar com cartão simulado

**Dados obrigatórios na requisição:**
```python
{
    "name": "Link de teste",
    "type": "order",  
    "payment_settings": {
        "accepted_payment_methods": ["credit_card", "pix", "boleto"],
        "credit_card": {
            "installments": [{"number": 1, "total": 10000}]
        }
    },
    "cart_settings": {
        "items": [{
            "amount": 10000,  # centavos
            "description": "Produto Teste",
            "quantity": 1
        }]
    },
    "customer_settings": {
        "customer_editable": True
    }
}
```

### FASE 4 — Pagamento via PIX
**Endpoint:** `POST /orders`

- [&check;] Serviço `payments/services/pix.py`:
  - `create_pix_order(amount, customer_data, expires_in)` → retorna QR code + copia-e-cola
- [&check;] View `pix_create` — cria pedido PIX e mostra QR code na página
- [&check;] Testar: criar com valor ≤ R$500 (sucesso) e > R$500 (falha)

**Dados obrigatórios:**
```python
{
    "items": [{
        "amount": 10000,  # centavos (≤ 50000 para sucesso no simulador)
        "description": "Teste PIX",
        "quantity": 1
    }],
    "customer": {
        "name": "Usuário Teste",
        "email": "usuarioteste@labce.com.br",
        "type": "individual",
        "document": "00000000000",
        "phones": {
            "mobile_phone": {
                "country_code": "55",
                "area_code": "11",
                "number": "999999999"
            }
        }
    },
    "payments": [{
        "payment_method": "pix",
        "pix": {
            "expires_in": 3600  # segundos
        }
    }]
}
```

**Resposta importante:**
- `response["charges"][0]["last_transaction"]["qr_code"]` → string para copia-e-cola
- `response["charges"][0]["last_transaction"]["qr_code_url"]` → imagem do QR code

### FASE 5 — Recorrência: Planos
**Endpoints:**
- `POST /plans` — Criar plano
- `GET /plans` — Listar planos
- `GET /plans/{plan_id}` — Obter plano
- `PUT /plans/{plan_id}` — Editar plano
- `DELETE /plans/{plan_id}` — Excluir plano

- [&check;] Serviço `payments/services/plans.py`:
  - `create_plan(name, description, interval, interval_count, items, payment_methods, billing_type, installments)`
  - `list_plans()`
  - `get_plan(plan_id)`
  - `delete_plan(plan_id)`
- [&check;] Views: `plan_create`, `plan_list`, `plan_detail`, `plan_delete`

**Dados obrigatórios para criar plano:**
```python
{
    "name": "Plano Básico",
    "description": "Plano mensal básico",
    "interval": "month",        # month, week, year
    "interval_count": 1,        # a cada 1 mês
    "billing_type": "prepaid",  # prepaid, postpaid, exact_day
    "payment_methods": ["credit_card"],
    "installments": [1],
    "items": [{
        "name": "Assinatura Mensal",
        "quantity": 1,
        "pricing_scheme": {
            "price": 2990  # R$ 29,90 em centavos
        }
    }]
}
```

### FASE 6 — Recorrência: Assinaturas
**Endpoints:**
- `POST /subscriptions` — Criar assinatura avulsa  
- `POST /subscriptions` (com `plan_id`) — Criar assinatura de plano
- `GET /subscriptions` — Listar
- `GET /subscriptions/{id}` — Obter
- `DELETE /subscriptions/{id}` — Cancelar
- `PATCH /subscriptions/{id}/card` — Editar cartão
- `PATCH /subscriptions/{id}/payment-method` — Editar meio de pagamento

- [&check;] Serviço `payments/services/subscriptions.py`:
  - `create_subscription_from_plan(plan_id, customer, card, payment_method)`
  - `create_standalone_subscription(items, customer, card, interval, interval_count, ...)`
  - `list_subscriptions()`
  - `get_subscription(subscription_id)`
  - `cancel_subscription(subscription_id)`
- [&check;] Views: `subscription_create`, `subscription_list`, `subscription_detail`, `subscription_cancel`

**Dados obrigatórios (assinatura de plano):**
```python
{
    "plan_id": "plan_xxxxxxxx",
    "payment_method": "credit_card",
    "customer": {
        "name": "Usuário Teste",
        "email": "usuarioteste@labce.com.br",
        "type": "individual",
        "document": "00000000000",
        "phones": {
            "mobile_phone": {
                "country_code": "55",
                "area_code": "11",
                "number": "999999999"
            }
        }
    },
    "card": {
        "number": "4000000000000010",  # cartão simulador sucesso
        "holder_name": "Usuário Teste",
        "exp_month": 12,
        "exp_year": 2030,
        "cvv": "123"
    }
}
```

**Dados obrigatórios (assinatura avulsa):**
```python
{
    "payment_method": "credit_card",
    "interval": "month",
    "interval_count": 1,
    "billing_type": "prepaid",
    "installments": 1,
    "customer": { ... },  # mesmo formato acima
    "card": { ... },      # mesmo formato acima
    "items": [{
        "description": "Assinatura mensal",
        "quantity": 1,
        "pricing_scheme": {
            "price": 2990
        }
    }]
}
```

### FASE 7 — Recorrência: Faturas
**Endpoints:**
- `POST /subscriptions/{subscription_id}/invoices` — Criar fatura (antecipada)
- `GET /subscriptions/{subscription_id}/invoices` — Listar faturas da assinatura
- `GET /invoices/{invoice_id}` — Obter fatura
- `DELETE /invoices/{invoice_id}` — Cancelar fatura

- [&check;] Serviço `payments/services/invoices.py`:
  - `list_invoices(subscription_id)`
  - `get_invoice(invoice_id)`
  - `cancel_invoice(invoice_id)`
- [&check;] Views: `invoice_list`, `invoice_detail`, `invoice_cancel`

### FASE 8 — Webhooks
**Conceito:** Pagar.me envia HTTP POST para URL configurada sempre que um evento ocorre.

- [&check;] View `webhook_receiver` — endpoint `POST /webhooks/pagarme/`
  - Recebe JSON do Pagar.me
  - Loga evento no console (print/logging)
  - Retorna HTTP 200 para confirmar recebimento
- [&check;] Configurar CSRF exemption (`@csrf_exempt`)
- [ ] Usar **ngrok** (ou similar) para expor URL local ao Pagar.me
  - `ngrok http 8000` → copiar URL HTTPS
  - Configurar webhook na Dashboard Pagar.me apontando para: `https://xxxx.ngrok.io/webhooks/pagarme/`

**Eventos relevantes para monitorar:**
| Evento | Descrição |
|---|---|
| `order.paid` | Pedido pago |
| `order.payment_failed` | Falha no pagamento do pedido |
| `order.canceled` | Pedido cancelado |
| `charge.paid` | Cobrança paga |
| `charge.payment_failed` | Falha na cobrança |
| `charge.refunded` | Cobrança estornada |
| `subscription.created` | Assinatura criada |
| `subscription.updated` | Assinatura atualizada |
| `subscription.canceled` | Assinatura cancelada |
| `invoice.created` | Fatura criada |
| `invoice.paid` | Fatura paga |
| `invoice.payment_failed` | Falha no pagamento da fatura |
| `invoice.canceled` | Fatura cancelada |
| `plan.created` | Plano criado |
| `checkout.created` | Checkout criado |
| `checkout.closed` | Checkout em processamento ou pago |
| `checkout.canceled` | Link de checkout expirado |

### FASE 9 — Dashboard Simples (Template HTML)
- [&check;] Página index com botões/links para cada ação:
  - Criar Checkout → redireciona para URL do Pagar.me
  - Criar Pedido PIX → mostra QR code
  - CRUD Planos → formulário simples
  - CRUD Assinaturas → formulário simples
  - Listar Faturas
  - Log de Webhooks recebidos
- [&check;] Usar templates Django simples (sem frameworks CSS, máximo um Bootstrap CDN)

---

## URLs do Projeto

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("payments.urls")),
]

# payments/urls.py
urlpatterns = [
    path("", views.index, name="index"),
    
    # Checkout
    path("checkout/create/", views.checkout_create, name="checkout_create"),
    
    # PIX
    path("pix/create/", views.pix_create, name="pix_create"),
    
    # Planos
    path("plans/", views.plan_list, name="plan_list"),
    path("plans/create/", views.plan_create, name="plan_create"),
    path("plans/<str:plan_id>/", views.plan_detail, name="plan_detail"),
    path("plans/<str:plan_id>/delete/", views.plan_delete, name="plan_delete"),
    
    # Assinaturas
    path("subscriptions/", views.subscription_list, name="subscription_list"),
    path("subscriptions/create/", views.subscription_create, name="subscription_create"),
    path("subscriptions/<str:sub_id>/", views.subscription_detail, name="subscription_detail"),
    path("subscriptions/<str:sub_id>/cancel/", views.subscription_cancel, name="subscription_cancel"),
    
    # Faturas
    path("subscriptions/<str:sub_id>/invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/<str:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    
    # Webhooks
    path("webhooks/pagarme/", views.webhook_receiver, name="webhook_receiver"),
]
```

---

## Dependências (`requirements.txt`)

```
django>=4.2,<5.0
requests>=2.31
python-decouple>=3.8
```

---

## Configuração do Ambiente de Teste

1. **Criar conta** no Pagar.me: https://id.pagar.me/
2. **Alternar para modo Teste** na Dashboard
3. **Copiar chaves** `sk_test_...` e `pk_test_...` para `.env`
4. **Selecionar simulador** em Configurações > Meios de pagamento na Dashboard
5. **Instalar ngrok** para webhooks: https://ngrok.com/
6. **Configurar webhook** na Dashboard apontando para URL do ngrok

---

## Ordem de Execução Recomendada

```
1. FASE 1 — Setup                    (~15 min)
2. FASE 2 — Client HTTP Base         (~20 min)
3. FASE 4 — PIX                      (~30 min)  ← mais simples, valida o client
4. FASE 3 — Checkout                 (~20 min)
5. FASE 5 — Planos                   (~30 min)
6. FASE 6 — Assinaturas              (~40 min)
7. FASE 7 — Faturas                  (~20 min)
8. FASE 8 — Webhooks                 (~30 min)
9. FASE 9 — Dashboard HTML           (~30 min)
```

**Tempo estimado total: ~3.5 horas**

---

## Notas

- Valores monetários na API são sempre em **centavos** (R$ 29,90 = `2990`)
- O simulador de cartão de crédito tem limite de **30 dias** para ações (captura, estorno)
- Recorrência aceita: Cartão de Crédito, Cartão de Débito (Pinless) e Boleto (não aceita PIX)
- Ao alterar um plano, as assinaturas vinculadas **não são alteradas automaticamente**
- Se `cycles` não for definido na assinatura, ela terá duração **infinita**
- Webhook deve retornar **HTTP 200** para confirmar recebimento; caso contrário, o Pagar.me reenvia
