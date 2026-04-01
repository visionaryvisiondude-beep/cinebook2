import uuid
from django.db import models
from django.conf import settings
from movies.models import Showtime
from seats.models import Seat


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    booking_ref = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings'
    )
    showtime = models.ForeignKey(Showtime, on_delete=models.PROTECT, related_name='bookings')
    seats = models.ManyToManyField(Seat, through='BookingSeat')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.booking_ref} — {self.user.email} — {self.status}"


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_seats')
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('booking', 'seat')
