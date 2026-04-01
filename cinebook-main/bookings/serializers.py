from rest_framework import serializers
from django.db import transaction
from django.core.cache import cache
from .models import Booking, BookingSeat
from seats.models import Seat, ShowtimeSeat
from movies.models import Showtime


class BookingSeatSerializer(serializers.ModelSerializer):
    row = serializers.CharField(source='seat.row', read_only=True)
    number = serializers.IntegerField(source='seat.number', read_only=True)
    seat_type = serializers.CharField(source='seat.seat_type', read_only=True)

    class Meta:
        model = BookingSeat
        fields = ('seat_id', 'row', 'number', 'seat_type', 'price_paid')


class BookingSerializer(serializers.ModelSerializer):
    booking_seats = BookingSeatSerializer(many=True, read_only=True)
    movie_title = serializers.CharField(source='showtime.movie.title', read_only=True)
    start_time = serializers.DateTimeField(source='showtime.start_time', read_only=True)
    theatre = serializers.CharField(source='showtime.screen.theatre.name', read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'booking_ref', 'movie_title', 'theatre', 'start_time',
            'booking_seats', 'total_amount', 'status', 'created_at',
        )
        read_only_fields = fields


class CreateBookingSerializer(serializers.Serializer):
    showtime_id = serializers.IntegerField()
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, max_length=10
    )

    def validate(self, attrs):
        showtime_id = attrs['showtime_id']
        seat_ids = attrs['seat_ids']
        user = self.context['request'].user

        try:
            showtime = Showtime.objects.select_related(
                'movie', 'screen', 'screen__theatre'
            ).get(id=showtime_id, is_active=True)
        except Showtime.DoesNotExist:
            raise serializers.ValidationError('Showtime not found or inactive.')

        attrs['showtime'] = showtime

        # Verify every seat is locked by this user in Redis
        for seat_id in seat_ids:
            lock_key = f"seat_lock:{showtime_id}:{seat_id}"
            locked_by = cache.get(lock_key)
            if locked_by != user.id:
                raise serializers.ValidationError(
                    f'Seat {seat_id} is not locked by you. Please lock seats before booking.'
                )

        # Verify seats belong to the showtime's screen and are still available in DB
        showtime_seats = ShowtimeSeat.objects.filter(
            showtime=showtime, seat_id__in=seat_ids
        ).select_related('seat')

        if showtime_seats.count() != len(seat_ids):
            raise serializers.ValidationError('One or more seats are invalid for this showtime.')

        unavailable = showtime_seats.exclude(status='available')
        if unavailable.exists():
            raise serializers.ValidationError(
                f'Seats already booked: {[ss.seat_id for ss in unavailable]}'
            )

        attrs['showtime_seats'] = showtime_seats
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        showtime = validated_data['showtime']
        showtime_seats = validated_data['showtime_seats']
        seat_ids = validated_data['seat_ids']

        # Calculate total — seat type determines price
        total = 0
        seat_prices = {}
        for ss in showtime_seats:
            if ss.seat.seat_type in ('premium', 'recliner'):
                price = showtime.price_premium
            else:
                price = showtime.price_regular
            seat_prices[ss.seat_id] = price
            total += price

        # Create the booking
        booking = Booking.objects.create(
            user=user,
            showtime=showtime,
            total_amount=total,
            status='pending',
        )

        # Create through-table rows and mark seats as booked
        for ss in showtime_seats:
            BookingSeat.objects.create(
                booking=booking,
                seat=ss.seat,
                price_paid=seat_prices[ss.seat_id],
            )
            ss.status = 'booked'
            ss.save(update_fields=['status'])

        # Release Redis locks — seats are now locked in DB
        for seat_id in seat_ids:
            cache.delete(f"seat_lock:{showtime.id}:{seat_id}")

        return booking
