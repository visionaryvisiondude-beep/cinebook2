from django.contrib import admin
from .models import Booking, BookingSeat


class BookingSeatInline(admin.TabularInline):
    model = BookingSeat
    extra = 0
    readonly_fields = ('seat', 'price_paid')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'user', 'showtime', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('booking_ref', 'user__email')
    readonly_fields = ('booking_ref', 'created_at', 'updated_at')
    inlines = [BookingSeatInline]
