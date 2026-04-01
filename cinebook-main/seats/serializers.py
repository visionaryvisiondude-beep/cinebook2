from rest_framework import serializers
from .models import Seat, ShowtimeSeat
from django.core.cache import cache
from django.conf import settings


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ('id', 'row', 'number', 'seat_type')


class ShowtimeSeatSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(read_only=True)
    is_locked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = ShowtimeSeat
        fields = ('id', 'seat', 'status', 'is_locked_by_me')

    def get_is_locked_by_me(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        lock_key = f"seat_lock:{obj.showtime_id}:{obj.seat_id}"
        locked_by = cache.get(lock_key)
        return locked_by == request.user.id
