from django.urls import path
from . import views

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
    path("subscriptions/create/", views.subscription_create,
         name="subscription_create"),
    path("subscriptions/<str:sub_id>/",
         views.subscription_detail, name="subscription_detail"),
    path("subscriptions/<str:sub_id>/cancel/",
         views.subscription_cancel, name="subscription_cancel"),

    # Faturas
    path("subscriptions/<str:sub_id>/invoices/",
         views.invoice_list, name="invoice_list"),
    path("invoices/<str:invoice_id>/",
         views.invoice_detail, name="invoice_detail"),
    path("invoices/<str:invoice_id>/cancel/",
         views.invoice_cancel, name="invoice_cancel"),

    # Webhooks
    path("webhooks/pagarme/", views.webhook_receiver, name="webhook_receiver"),
    path("webhooks/log/", views.webhook_log, name="webhook_log"),
]
