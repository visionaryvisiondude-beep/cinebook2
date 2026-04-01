"""
BOOKINGS ENDPOINTS
==================
POST  /api/bookings/                      Create a new booking (seats must be locked first)
GET   /api/bookings/my/                   List all bookings for the authenticated user
GET   /api/bookings/{booking_ref}/        Get a single booking by UUID ref
POST  /api/bookings/{booking_ref}/cancel/ Cancel a pending or confirmed booking

Create booking body:
  { "showtime_id": 1, "seat_ids": [1, 2, 3] }

After creating a booking its status is "pending" until payment is confirmed.
Cancelling frees the seats back to "available" and triggers a cancellation email.
"""
from django.urls import path
from .views import CreateBookingView, MyBookingsView, BookingDetailView, CancelBookingView

app_name = 'bookings'

urlpatterns = [
    path('',                             CreateBookingView.as_view(),  name='create-booking'),
    path('my/',                          MyBookingsView.as_view(),     name='my-bookings'),
    path('<uuid:booking_ref>/',          BookingDetailView.as_view(),  name='booking-detail'),
    path('<uuid:booking_ref>/cancel/',   CancelBookingView.as_view(),  name='cancel-booking'),
]
