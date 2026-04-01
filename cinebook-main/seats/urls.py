"""
SEATS ENDPOINTS
===============
GET   /api/seats/showtime/{showtime_id}/          Full seat map grouped by row, with live availability
POST  /api/seats/showtime/{showtime_id}/lock/     Lock selected seats for 5 min (must call before booking)
POST  /api/seats/showtime/{showtime_id}/unlock/   Release your own locks (e.g. user abandons cart)

Lock body:   { "seat_ids": [1, 2, 3] }
Unlock body: { "seat_ids": [1, 2, 3] }

Seat status values returned in seat map:
  available  — free to select
  locked     — held by another user (5-min window)
  booked     — permanently reserved
  
is_locked_by_me field is true when the authenticated user holds the lock on that seat.
"""
from django.urls import path
from .views import ShowtimeSeatMapView, lock_seats, unlock_seats

app_name = 'seats'

urlpatterns = [
    path('showtime/<int:showtime_id>/',         ShowtimeSeatMapView.as_view(), name='seat-map'),
    path('showtime/<int:showtime_id>/lock/',    lock_seats,                    name='lock-seats'),
    path('showtime/<int:showtime_id>/unlock/',  unlock_seats,                  name='unlock-seats'),
]
