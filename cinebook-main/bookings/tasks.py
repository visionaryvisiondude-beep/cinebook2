from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_booking_confirmation(self, booking_id):
    """Send booking confirmation email asynchronously."""
    from .models import Booking
    try:
        booking = Booking.objects.select_related(
            'user', 'showtime__movie', 'showtime__screen__theatre'
        ).prefetch_related('booking_seats__seat').get(id=booking_id)

        seats_str = ', '.join(
            f"{bs.seat.row}{bs.seat.number}"
            for bs in booking.booking_seats.all()
        )

        subject = f"CineBook — Booking Confirmed! #{str(booking.booking_ref)[:8].upper()}"
        message = f"""
Hi {booking.user.username},

Your booking is confirmed!

Movie      : {booking.showtime.movie.title}
Theatre    : {booking.showtime.screen.theatre.name}
Screen     : {booking.showtime.screen.name}
Date & Time: {booking.showtime.start_time.strftime('%d %b %Y, %I:%M %p')}
Seats      : {seats_str}
Total Paid : ₹{booking.total_amount}
Booking Ref: {booking.booking_ref}

Enjoy the show!
— Team CineBook
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def send_booking_cancellation(booking_id):
    """Send cancellation email."""
    from .models import Booking
    try:
        booking = Booking.objects.select_related('user', 'showtime__movie').get(id=booking_id)
        send_mail(
            subject=f"CineBook — Booking Cancelled #{str(booking.booking_ref)[:8].upper()}",
            message=f"Hi {booking.user.username},\n\nYour booking for {booking.showtime.movie.title} has been cancelled.\nRef: {booking.booking_ref}\n\n— Team CineBook",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=True,
        )
    except Exception:
        pass
