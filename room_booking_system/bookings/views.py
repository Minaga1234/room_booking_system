from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Booking
from .serializers import BookingSerializer
from penalties.models import Penalty
from analytics.models import Analytics
from datetime import date
from django.utils import timezone
from notifications.models import Notification
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.db.models import Count
from penalties.views import PenaltyViewSet

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Fetch bookings for the currently logged-in user.
        """
        user = request.user
        user_bookings = Booking.objects.filter(user=user)
        serializer = self.get_serializer(user_bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a pending booking and notify the user.
        """
        booking = self.get_object()
        if booking.status == 'approved':
            return Response({"message": "Booking is already approved."}, status=400)

        booking.status = 'approved'
        booking.is_approved = True
        booking.save()

        Notification.objects.create(
            user=booking.user,
            message=f"Your booking for {booking.room.name} has been approved.",
            notification_type='booking_update'
        )
        return Response({"message": "Booking approved."})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def cancel(self, request, pk=None):
        """Cancel a booking and apply penalties if needed."""
        booking = self.get_object()
        if booking.status not in ['canceled', 'checked_in']:
            PenaltyViewSet.apply_penalty(booking)

        booking.status = 'canceled'
        booking.save()

        Notification.objects.create(
            user=booking.user,
            message=f"Your booking for {booking.room.name} has been canceled.",
            notification_type='booking_update'
        )
        return Response({"message": "Booking canceled."})

    def check_for_penalty(self, booking):
        """
        Check if a penalty should be applied for late cancellation or no-show.
        """
        if booking.end_time < timezone.now() and not booking.is_approved:
            penalty, created = Penalty.objects.get_or_create(
                user=booking.user,
                booking=booking,
                reason="Late cancellation or no-show",
                defaults={
                    "amount": 50.00,
                    "status": "unpaid"
                }
            )
            if created:
                Notification.objects.create(
                    user=booking.user,
                    message=f"A penalty of ${penalty.amount} has been imposed for {penalty.reason}.",
                    notification_type='penalty_reminder'
                )

    def destroy(self, request, *args, **kwargs):
        """
        Apply penalty for late cancellation before deleting a booking.
        """
        booking = self.get_object()
        self.check_for_penalty(booking)
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create a new booking, update analytics, and notify the user.
        """
        booking = serializer.save()

        try:
            analytics, created = Analytics.objects.get_or_create(
                room=booking.room,
                date=date.today()
            )
            analytics.total_bookings += 1
            analytics.save()
        except Exception as e:
            print(f"Analytics update failed: {e}")

        Notification.objects.create(
            user=booking.user,
            message=f"Your booking for {booking.room.name} has been successfully created.",
            notification_type='booking_update'
        )

    def check_in(self, request, pk=None):
        """
        Mark a booking as checked in and update analytics.
        """
        """
        Mark a booking as checked in and update analytics.
        """
        booking = self.get_object()

        try:
            # Update analytics
            analytics, created = Analytics.objects.get_or_create(
                room=booking.room,
                date=date.today()
            )
            analytics.total_checkins += 1
            analytics.save()
        except Exception as e:
            print(f"Check-in analytics update failed for booking {booking.id}: {e}")

        # Notify the user about the check-in
        Notification.objects.create(
            user=booking.user,
            message=f"You have successfully checked in for your booking at {booking.room.name}.",
            notification_type='booking_update'
        )
        try:
            # Update analytics
            analytics, created = Analytics.objects.get_or_create(
                room=booking.room,
                date=date.today()
            )
            analytics.total_checkins += 1
            analytics.save()
        except Exception as e:
            print(f"Check-in analytics update failed for booking {booking.id}: {e}")

        # Notify the user about the check-in
        Notification.objects.create(
            user=booking.user,
            message=f"You have successfully checked in for your booking at {booking.room.name}.",
            notification_type='booking_update'
        )

        return Response({"message": "Check-in successful"})

    def validate_peak_usage(room, start_time):
        """
        Restrict bookings during peak hours.
        """
        analytics = Analytics.objects.filter(room=room, date=start_time.date()).first()
        if analytics and analytics.utilization_rate > 80:  # Threshold for peak usage
            raise ValidationError("Room is currently in high demand. Booking restrictions apply.")
        
    @action(detail=False, methods=['get'])
    def popular_rooms(self, request):
        """
        Get the most popular rooms based on booking counts.
        """
        popular_rooms = Booking.objects.values('room__name').annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')
        return Response(popular_rooms)

    @action(detail=False, methods=['get'])
    def traffic_data(self, request):
        """
        Get traffic data based on bookings and check-ins.
        """
        analytics = Analytics.objects.all().values('room__name', 'date', 'total_bookings', 'total_checkins')
        return Response(analytics)
    def apply_penalty(self, booking, reason="Late cancellation or no-show"):
        """
        Apply penalty to the user for specific reasons.
        """
        penalty, created = Penalty.objects.get_or_create(
            user=booking.user,
            booking=booking,
            reason=reason,
            defaults={
                "amount": booking.calculate_penalty(),
                "status": "unpaid"
            }
        )
        if created:
            Notification.objects.create(
                user=booking.user,
                message=f"A penalty of ${penalty.amount} has been imposed for {penalty.reason}.",
                notification_type='penalty_reminder'
            )
