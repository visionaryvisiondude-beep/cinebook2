from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('payment_id', 'booking__booking_ref', 'gateway_payment_id')
    readonly_fields = ('payment_id', 'created_at', 'updated_at')
