from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from bookings.models import Booking
from .serializers import InitiatePaymentSerializer, ConfirmPaymentSerializer
import uuid


class InitiatePaymentView(APIView):
    """
    POST /api/payments/initiate/
    Body: { "booking_ref": "<uuid>" }

    In production: create a Razorpay order here and return order_id.
    For dev/demo: returns a mock order_id immediately.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_ref = serializer.validated_data['booking_ref']
        booking = get_object_or_404(
            Booking, booking_ref=booking_ref, user=request.user, status='pending'
        )

        # Idempotent — if payment already initiated, return existing
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={'amount': booking.total_amount, 'status': 'initiated'}
        )

        # --- Razorpay integration (uncomment when ready) ---
        # import razorpay
        # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # order = client.order.create({
        #     'amount': int(booking.total_amount * 100),  # paise
        #     'currency': 'INR',
        #     'receipt': str(booking.booking_ref),
        # })
        # payment.gateway_order_id = order['id']
        # payment.save()

        # Mock response for dev
        mock_order_id = f"order_mock_{str(uuid.uuid4())[:8]}"
        if created:
            payment.gateway_order_id = mock_order_id
            payment.save(update_fields=['gateway_order_id'])

        return Response({
            'payment_id': str(payment.payment_id),
            'booking_ref': str(booking.booking_ref),
            'amount': str(booking.total_amount),
            'currency': 'INR',
            'gateway_order_id': payment.gateway_order_id,
            'status': payment.status,
            'message': 'Payment initiated. Use payment_id to confirm payment.',
            # Frontend sends these to Razorpay checkout
            # 'razorpay_key': settings.RAZORPAY_KEY_ID,
        })


class ConfirmPaymentView(APIView):
    """
    POST /api/payments/confirm/
    Body: {
        "payment_id": "<uuid>",
        "gateway_payment_id": "pay_xxx",
        "gateway_signature": "sig_xxx"
    }

    In production: verify Razorpay signature here.
    For dev/demo: any non-empty gateway_payment_id marks payment successful.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ConfirmPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_id = serializer.validated_data['payment_id']
        gateway_payment_id = serializer.validated_data.get('gateway_payment_id', '')
        gateway_signature = serializer.validated_data.get('gateway_signature', '')

        payment = get_object_or_404(
            Payment,
            payment_id=payment_id,
            booking__user=request.user,
        )

        if payment.status == 'success':
            return Response({'detail': 'Payment already confirmed.'})

        # --- Razorpay signature verification (uncomment in production) ---
        # import razorpay, hmac, hashlib
        # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # try:
        #     client.utility.verify_payment_signature({
        #         'razorpay_order_id': payment.gateway_order_id,
        #         'razorpay_payment_id': gateway_payment_id,
        #         'razorpay_signature': gateway_signature,
        #     })
        # except razorpay.errors.SignatureVerificationError:
        #     payment.status = 'failed'
        #     payment.save()
        #     return Response({'detail': 'Signature verification failed.'}, status=400)

        # Mock: accept any non-empty gateway_payment_id
        if not gateway_payment_id or gateway_payment_id == '':
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            return Response({'detail': 'Payment failed.'}, status=status.HTTP_400_BAD_REQUEST)

        payment.gateway_payment_id = gateway_payment_id or ''
        payment.gateway_signature = gateway_signature or ''
        payment.status = 'success'
        payment.save(update_fields=['gateway_payment_id', 'gateway_signature', 'status'])

        # Confirm the booking
        booking = payment.booking
        booking.status = 'confirmed'
        booking.save(update_fields=['status'])

        # Release seat locks (they should already be released at booking creation,
        # but this ensures cleanup if payment was retried)
        from seats.models import ShowtimeSeat
        from django.core.cache import cache
        seat_ids = booking.booking_seats.values_list('seat_id', flat=True)
        for seat_id in seat_ids:
            cache.delete(f"seat_lock:{booking.showtime.id}:{seat_id}")

        return Response({
            'detail': 'Payment successful! Booking confirmed.',
            'booking_ref': str(booking.booking_ref),
            'status': 'confirmed',
            'payment_id': str(payment.payment_id),
        })


class PaymentStatusView(APIView):
    """
    GET /api/payments/status/{payment_id}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(
            Payment, payment_id=payment_id, booking__user=request.user
        )
        return Response({
            'payment_id': str(payment.payment_id),
            'status': payment.status,
            'amount': str(payment.amount),
            'booking_ref': str(payment.booking.booking_ref),
            'booking_status': payment.booking.status,
        })
