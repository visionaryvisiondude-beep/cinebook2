from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Booking
from .serializers import BookingSerializer, CreateBookingSerializer
from .tasks import send_booking_cancellation
from seats.models import ShowtimeSeat


class CreateBookingView(generics.CreateAPIView):
    """
    POST /api/bookings/
    Creates booking from Redis-locked seats. Marks seats as booked atomically.
    """
    serializer_class = CreateBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        # Fire async email — silently skip if Redis not available
        try:
            from .tasks import send_booking_confirmation
            send_booking_confirmation.delay(booking.id)
        except Exception:
            pass
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )
class MyBookingsView(generics.ListAPIView):
    """
    GET /api/bookings/my/
    Returns all bookings for the authenticated user.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related(
            'showtime__movie', 'showtime__screen__theatre'
        ).prefetch_related('booking_seats__seat')


class BookingDetailView(generics.RetrieveAPIView):
    """
    GET /api/bookings/{booking_ref}/
    Retrieve a single booking by UUID ref.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'booking_ref'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            'showtime__movie', 'showtime__screen__theatre'
        ).prefetch_related('booking_seats__seat')


class CancelBookingView(APIView):
    """
    POST /api/bookings/{booking_ref}/cancel/
    Cancel a pending booking and free the seats.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_ref):
        booking = get_object_or_404(
            Booking, booking_ref=booking_ref, user=request.user
        )

        if booking.status not in ('pending', 'confirmed'):
            return Response(
                {'detail': 'This booking cannot be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Free the seats in ShowtimeSeat
        seat_ids = booking.booking_seats.values_list('seat_id', flat=True)
        ShowtimeSeat.objects.filter(
            showtime=booking.showtime, seat_id__in=seat_ids
        ).update(status='available')

        booking.status = 'cancelled'
        booking.save(update_fields=['status'])

        send_booking_cancellation.delay(booking.id)

        return Response({'detail': 'Booking cancelled successfully.'})
