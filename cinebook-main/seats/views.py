from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Seat, ShowtimeSeat
from .serializers import ShowtimeSeatSerializer
from movies.models import Showtime


class ShowtimeSeatMapView(generics.ListAPIView):
    """
    GET /api/seats/showtime/{showtime_id}/
    Returns the full seat map for a showtime with availability.
    """
    serializer_class = ShowtimeSeatSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        showtime_id = self.kwargs['showtime_id']
        return ShowtimeSeat.objects.filter(
            showtime_id=showtime_id
        ).select_related('seat').order_by('seat__row', 'seat__number')

    def list(self, request, *args, **kwargs):
        showtime_id = self.kwargs['showtime_id']
        showtime = get_object_or_404(Showtime, id=showtime_id)
        qs = self.get_queryset()

        # Reflect Redis locks into status for the response
        result = []
        for ss in qs:
            lock_key = f"seat_lock:{showtime_id}:{ss.seat_id}"
            locked_by = cache.get(lock_key)
            data = ShowtimeSeatSerializer(ss, context={'request': request}).data
            if ss.status == 'available' and locked_by and locked_by != request.user.id:
                data['status'] = 'locked'
            result.append(data)

        # Group by row for easy frontend rendering
        rows = {}
        for seat_data in result:
            row = seat_data['seat']['row']
            rows.setdefault(row, []).append(seat_data)

        return Response({
            'showtime_id': showtime_id,
            'movie': showtime.movie.title,
            'start_time': showtime.start_time,
            'price_regular': showtime.price_regular,
            'price_premium': showtime.price_premium,
            'rows': rows,
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def lock_seats(request, showtime_id):
    """
    POST /api/seats/showtime/{showtime_id}/lock/
    Body: { "seat_ids": [1, 2, 3] }
    Locks selected seats in Redis for SEAT_LOCK_TTL seconds (default 5 min).
    """
    seat_ids = request.data.get('seat_ids', [])
    if not seat_ids:
        return Response({'detail': 'No seats provided.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(seat_ids) > 10:
        return Response({'detail': 'Cannot lock more than 10 seats at once.'}, status=status.HTTP_400_BAD_REQUEST)

    showtime = get_object_or_404(Showtime, id=showtime_id, is_active=True)
    ttl = getattr(settings, 'SEAT_LOCK_TTL', 300)

    locked = []
    failed = []

    for seat_id in seat_ids:
        ss = ShowtimeSeat.objects.filter(
            showtime=showtime, seat_id=seat_id
        ).select_related('seat').first()

        if not ss:
            failed.append({'seat_id': seat_id, 'reason': 'Not found'})
            continue

        if ss.status == 'booked':
            failed.append({'seat_id': seat_id, 'reason': 'Already booked'})
            continue

        lock_key = f"seat_lock:{showtime_id}:{seat_id}"
        existing_lock = cache.get(lock_key)

        if existing_lock and existing_lock != request.user.id:
            failed.append({'seat_id': seat_id, 'reason': 'Locked by another user'})
            continue

        # Acquire or refresh lock
        cache.set(lock_key, request.user.id, timeout=ttl)
        locked.append(seat_id)

    if failed:
        # Release any locks we just acquired since the full selection failed
        for seat_id in locked:
            cache.delete(f"seat_lock:{showtime_id}:{seat_id}")
        return Response({
            'detail': 'Some seats could not be locked. Please choose again.',
            'failed': failed,
        }, status=status.HTTP_409_CONFLICT)

    return Response({
        'detail': 'Seats locked successfully.',
        'locked_seat_ids': locked,
        'expires_in_seconds': ttl,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlock_seats(request, showtime_id):
    """
    POST /api/seats/showtime/{showtime_id}/unlock/
    Body: { "seat_ids": [1, 2, 3] }
    Explicitly release locks held by the current user (e.g. on cart abandon).
    """
    seat_ids = request.data.get('seat_ids', [])
    released = []
    for seat_id in seat_ids:
        lock_key = f"seat_lock:{showtime_id}:{seat_id}"
        if cache.get(lock_key) == request.user.id:
            cache.delete(lock_key)
            released.append(seat_id)

    return Response({'released_seat_ids': released})
