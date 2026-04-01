"""
PAYMENTS ENDPOINTS
==================
POST  /api/payments/initiate/              Initiate payment for a pending booking
POST  /api/payments/confirm/               Confirm payment (verify gateway response)
GET   /api/payments/status/{payment_id}/   Get current payment + booking status

Initiate body:
  { "booking_ref": "<uuid>" }

Confirm body:
  {
    "payment_id": "<uuid>",
    "gateway_payment_id": "pay_xxx",   (from Razorpay / mock)
    "gateway_signature": "sig_xxx"     (from Razorpay / empty for mock)
  }

On successful confirm the booking status changes from "pending" → "confirmed"
and a confirmation email is dispatched via Celery.

For Razorpay integration: uncomment the client calls in payments/views.py
and set RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET in your .env file.
"""
from django.urls import path
from .views import InitiatePaymentView, ConfirmPaymentView, PaymentStatusView

app_name = 'payments'

urlpatterns = [
    path('initiate/',            InitiatePaymentView.as_view(),  name='initiate-payment'),
    path('confirm/',             ConfirmPaymentView.as_view(),   name='confirm-payment'),
    path('status/<uuid:payment_id>/', PaymentStatusView.as_view(), name='payment-status'),
]
