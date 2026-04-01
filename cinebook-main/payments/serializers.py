from rest_framework import serializers
from .models import Payment


class InitiatePaymentSerializer(serializers.Serializer):
    booking_ref = serializers.UUIDField()


class ConfirmPaymentSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField()
    gateway_payment_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gateway_signature = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class PaymentSerializer(serializers.ModelSerializer):
    booking_ref = serializers.UUIDField(source='booking.booking_ref', read_only=True)

    class Meta:
        model = Payment
        fields = ('payment_id', 'booking_ref', 'amount', 'status', 'gateway_order_id', 'created_at')
        read_only_fields = fields