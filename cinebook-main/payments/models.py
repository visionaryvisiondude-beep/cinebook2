import uuid
from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='initiated')
    # Store gateway response (Razorpay order_id, payment_id etc.)
    gateway_order_id = models.CharField(max_length=200, blank=True)
    gateway_payment_id = models.CharField(max_length=200, blank=True)
    gateway_signature = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_id} — {self.booking.booking_ref} — {self.status}"
