from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Booking
from .serializers import BookingSerializer
from penalties.models import Penalty
from analytics.models import Analytics
from datetime import date

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        user = request.user
        user_bookings = Booking.objects.filter(user=user)
        serializer = self.get_serializer(user_bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'approved'
        booking.is_approved = True
        booking.save()
        return Response({"message": "Booking approved"})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'canceled'
        booking.save()
        return Response({"message": "Booking canceled"})
    
    def check_for_penalty(self, booking):
        if booking.end_time < timezone.now() and not booking.is_approved:
            Penalty.objects.create(
                user=booking.user,
                booking=booking,
                reason="Late cancellation or no-show",
                amount=50.00,  # Set your penalty amount
                status="unpaid"
            )

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        self.check_for_penalty(booking)
        return super().destroy(request, *args, **kwargs)
    
    def update_booking_status(self, booking, status):
        booking.status = status
        booking.save()

        # Create a notification
        Notification.objects.create(
            user=booking.user,
            message=f"Your booking for {booking.room.name} has been {status}.",
            notification_type='booking_update'
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        booking = self.get_object()
        self.update_booking_status(booking, 'approved')
        return Response({"message": "Booking approved"})

    def perform_create(self, serializer):
        booking = serializer.save()

        # Update analytics
        analytics, created = Analytics.objects.get_or_create(
            room=booking.room,
            date=date.today()
        )
        analytics.total_bookings += 1
        analytics.save()

    def check_in(self, request, pk=None):
        booking = self.get_object()
        # Logic for check-in...

        # Update analytics
        analytics, created = Analytics.objects.get_or_create(
            room=booking.room,
            date=date.today()
        )
        analytics.total_checkins += 1
        analytics.save()

        return Response({"message": "Check-in successful"})