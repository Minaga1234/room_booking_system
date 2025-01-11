from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from .models import Penalty
from .serializers import PenaltySerializer
from bookings.models import Booking
from django.utils import timezone
from rest_framework.decorators import api_view
from django.db.models import Count, Q
from django.utils.timezone import now, timedelta
import csv
from django.http import HttpResponse
from datetime import datetime, timezone  # Update the import
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware, get_default_timezone
from django.db.models import Case, When, IntegerField


class PenaltyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        print(f"Pagination Response: count={self.page.paginator.count}, page_size={self.page_size}, next={self.get_next_link()}, previous={self.get_previous_link()}")
        return Response({
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PenaltyPagination

    def get_queryset(self):
        queryset = Penalty.objects.all()  # Fetch all penalties for admin

        # Get query parameters
        status = self.request.query_params.get('status', 'all')  # Default to 'all'
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        # Apply status filter
        if status == 'unpaid':
            # Include only 'unpaid' and 'Active'
            queryset = queryset.filter(status__in=['unpaid', 'Active'])
        elif status == 'paid':
            # Include only 'paid'
            queryset = queryset.filter(status='paid')

        # Apply date filters
        if start_date:
            try:
                parsed_start_date = parse_date(start_date)
                if parsed_start_date:
                    start_datetime = make_aware(datetime.combine(parsed_start_date, datetime.min.time()))
                    queryset = queryset.filter(created_at__gte=start_datetime)
            except Exception as e:
                print(f"Invalid start_date format: {e}")

        if end_date:
            try:
                parsed_end_date = parse_date(end_date)
                if parsed_end_date:
                    end_datetime = make_aware(datetime.combine(parsed_end_date, datetime.max.time()))
                    queryset = queryset.filter(created_at__lte=end_datetime)
            except Exception as e:
                print(f"Invalid end_date format: {e}")

        # Order by created_at descending
        return queryset.order_by('-created_at')







    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_penalties(self, request):
        user = self.request.user

        # Query all penalties for the user
        all_penalties = Penalty.objects.filter(user=user).order_by('-created_at')

        # Calculate active penalties count (global, not tied to pagination)
        active_penalties_count = Penalty.objects.filter(user=user, status__in=['unpaid', 'Active']).count()



        # Debug logs
        print(f"Total Penalties for {user}: {all_penalties.count()}")
        print(f"Active Penalties for {user}: {active_penalties}")
        print(f"Active Penalties Count: {active_penalties_count}")
        print(f"Active Penalties Count Sent to Frontend: {active_penalties_count}")
        

        
        # Paginate all penalties
        page = self.paginate_queryset(all_penalties)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'activePenalties': active_penalties_count,  # Include the global count here
            })

        serializer = self.get_serializer(all_penalties, many=True)
        return Response({
            'results': serializer.data,
            'activePenalties': active_penalties_count,  # Include the global count here
        })





    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def request_review(self, request, pk=None):
        """Allow users to request a review of their penalties."""
        penalty = self.get_object()
        if penalty.user != request.user:
            return Response({"error": "You can only request a review for your own penalties."}, status=403)

        # Example logic for requesting a review
        penalty.status = "review_requested"
        penalty.save()
        return Response({"message": "Review request submitted successfully."})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def resolve(self, request, pk=None):
        penalty = self.get_object()
        if penalty.status in ['unpaid', 'Active']:  # Match frontend status
            penalty.status = 'paid'
            penalty.save()
            return Response({"message": "Penalty resolved successfully."}, status=200)
        return Response({"error": "Penalty is already resolved or invalid status."}, status=400)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        penalty = self.get_object()
        if penalty.status == 'unpaid':
            penalty.status = 'paid'
            penalty.save()
            return Response({"message": "Penalty marked as paid."})
        return Response({"message": "Penalty is already paid."}, status=400)

    @action(detail=False, methods=['get'])
    def user_penalties(self, request):
        user = request.user
        penalties = Penalty.objects.filter(user=user)
        page = self.paginate_queryset(penalties)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(penalties, many=True)
        return Response(serializer.data)

    @staticmethod
    def apply_penalty(booking):
        """Apply penalty for late cancellation or no-show."""
        if booking.status == 'canceled' and booking.end_time < timezone.now():
            Penalty.create_penalty(
                user=booking.user,
                booking=booking,
                reason="Late cancellation",
                amount=50.00
            )
        elif booking.status == 'pending' and booking.start_time < timezone.now():
            Penalty.create_penalty(
                user=booking.user,
                booking=booking,
                reason="No-show",
                amount=100.00
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def download_report(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="penalties_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Penalty ID', 'User', 'Booking', 'Reason', 'Amount', 'Status', 'Created At'])
        for penalty in self.get_queryset():
            writer.writerow([
                penalty.id,
                penalty.user.email,
                penalty.booking.id if penalty.booking else "N/A",
                penalty.reason,
                penalty.amount,
                penalty.status,
                penalty.created_at,
            ])
        return response
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve_review(self, request, pk=None):
        penalty = self.get_object()
        if penalty.status == 'review_requested':
            penalty.status = 'resolved'
            penalty.save()
            # Send notification to user
            Notification.create_notification(
                user=penalty.user,
                message=f"Your penalty review (ID: {penalty.id}) has been approved.",
                notification_type='penalty_update'
            )
            return Response({"message": "Penalty review approved successfully."})
        return Response({"error": "Invalid status for approval."}, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject_review(self, request, pk=None):
        penalty = self.get_object()
        if penalty.status == 'review_requested':
            penalty.status = 'unpaid'  # Or revert to its previous state
            penalty.save()
            # Send notification to user
            Notification.create_notification(
                user=penalty.user,
                message=f"Your penalty review (ID: {penalty.id}) has been rejected.",
                notification_type='penalty_update'
            )
            return Response({"message": "Penalty review rejected successfully."})
        return Response({"error": "Invalid status for rejection."}, status=400)




@api_view(['GET'])
def penalties_overview(request):
    print("Overview endpoint accessed")
    """Provide an overview of penalties for the dashboard."""
    active_penalties = Penalty.objects.filter(status__in=['unpaid', 'Active']).count()
    new_penalties = Penalty.objects.filter(created_at__gte=now() - timedelta(days=7)).count()
    resolved_penalties = Penalty.objects.filter(status='paid').count()
    repeat_offenders = Penalty.objects.values('user').annotate(count=Count('user')).filter(count__gt=1).count()

    # Debugging output
    print(f"Active Penalties: {active_penalties}")
    print(f"New Penalties: {new_penalties}")
    print(f"Resolved Penalties: {resolved_penalties}")
    print(f"Repeat Offenders: {repeat_offenders}")

    return Response({
        'active_penalties': active_penalties,
        'new_penalties': new_penalties,
        'resolved_penalties': resolved_penalties,
        'repeat_offenders': repeat_offenders,
    })
