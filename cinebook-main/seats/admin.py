from django.contrib import admin
from .models import Seat, ShowtimeSeat


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('screen', 'row', 'number', 'seat_type')
    list_filter = ('seat_type', 'screen__theatre')
    search_fields = ('screen__theatre__name', 'screen__name')


@admin.register(ShowtimeSeat)
class ShowtimeSeatAdmin(admin.ModelAdmin):
    list_display = ('showtime', 'seat', 'status')
    list_filter = ('status',)
    search_fields = ('showtime__movie__title',)
