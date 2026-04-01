from django.db import models
from movies.models import Screen, Showtime


class Seat(models.Model):
    SEAT_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('premium', 'Premium'),
        ('recliner', 'Recliner'),
    ]

    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=2)        # e.g. "A", "B", "AA"
    number = models.PositiveIntegerField()       # e.g. 1, 2, 3
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPE_CHOICES, default='regular')

    class Meta:
        unique_together = ('screen', 'row', 'number')
        ordering = ['row', 'number']

    def __str__(self):
        return f"{self.screen} | {self.row}{self.number} ({self.seat_type})"


class ShowtimeSeat(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('locked', 'Locked'),       # held in Redis for 5 min
        ('booked', 'Booked'),
    ]

    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='showtime_seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='showtime_seats')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    class Meta:
        unique_together = ('showtime', 'seat')
        ordering = ['seat__row', 'seat__number']

    def __str__(self):
        return f"{self.showtime} | {self.seat} — {self.status}"
