from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count
from datetime import date, timedelta
from .models import Booking, Room
from .serializers import BookingSerializer
from analytics.models import Analytics
from notifications.models import Notification
from penalties.views import PenaltyViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from users.models import CustomUser 

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """
        Custom permissions based on action.
        """
        if self.action in ['create']:
            return [AllowAny()]  # Allow anyone to create a booking
        return [IsAuthenticated()]  # Require authentication for other actions

    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Fetch bookings for the currently logged-in user.
        """
        user_email = request.GET.get('email')
        if not user_email:
            return Response({"error": "Email is required to fetch bookings."}, status=400)

        user_bookings = Booking.objects.filter(user__email=user_email)
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
        """
        Cancel a booking and apply penalties if needed.
        """
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel_own_booking(self, request, pk=None):
        """
        Allow booking owners to cancel their own bookings.
        """
        booking = self.get_object()
        if booking.user != request.user:
            return Response({"error": "You can only cancel your own bookings."}, status=403)

        if booking.status == 'canceled':
            return Response({"message": "This booking is already canceled."}, status=400)

        booking.status = 'canceled'
        booking.save()

        Notification.objects.create(
            user=booking.user,
            message=f"Your booking for {booking.room.name} has been canceled.",
            notification_type='booking_update'
        )
        return Response({"message": "Your booking has been successfully canceled."})

    def perform_create(self, serializer):
        user_email = self.request.data.get("email")
        user = self.request.user  # Ensure the user is retrieved correctly
        serializer.save(user=user)

        if user_email:
            try:
                user = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                raise ValidationError("User not found. Please register first.")
        else:
            if self.request.user.is_authenticated:
                user = self.request.user
            else:
                raise ValidationError("Email or authentication token required to identify the user.")

        # Get the booking start date from the serializer data
        start_time = serializer.validated_data.get('start_time')
        if not start_time:
            raise ValidationError("Start time is required for the booking.")

        # Enforce role-based booking date rules
        role = user.role if user else "guest"
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        if role == 'student':
            # Students can only book for today
            if start_time.date() != today:
                raise ValidationError("Students can only book for today.")
        elif role == 'staff':
            # Staff can only book for today or tomorrow
            if start_time.date() not in [today, tomorrow]:
                raise ValidationError("Lecturers can only book for today or tomorrow.")
        elif role == 'admin':
            # Admins can book for any date (no restrictions)
            pass
        else:
            raise ValidationError("Unknown user role. Please contact support.")

        # Save the booking with the associated user
        serializer.save(user=user)
        
    @action(detail=False, methods=['get'])
    def calendar_events(self, request):
        bookings = Booking.objects.all()
        events = [
            {
                "id": booking.id,
                "title": f"{booking.room.name} - {booking.user.username}",
                "start": booking.start_time.isoformat(),
                "end": booking.end_time.isoformat()
            }
            for booking in bookings
        ]
        return Response(events)

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
    
    
