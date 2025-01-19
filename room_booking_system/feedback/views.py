from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg
from rest_framework.views import APIView
from django.db.models import Q
from .models import Feedback
from .serializers import FeedbackSerializer
import csv
from django.http import HttpResponse
from rest_framework.permissions import AllowAny



class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle Feedback operations
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]  # No authentication required for basic access

    def perform_create(self, serializer):
        """
        Save feedback data with additional fields and perform sentiment analysis.
        """
        user = self.request.user if self.request.user.is_authenticated else None
        full_name = user.username if user else "Anonymous User"
        student_id = str(user.id) if user else "0"

        feedback = serializer.save(
            user=user,
            full_name=full_name,
            student_id=student_id
        )

        # Perform Sentiment Analysis
        sentiment, sentiment_details = self.analyze_sentiment(feedback.content)
        feedback.sentiment = sentiment
        feedback.sentiment_details = sentiment_details  # Add detailed analysis
        feedback.save()

    @staticmethod
    def analyze_sentiment(content):
        """
        Analyze the sentiment of the feedback content using VADER Sentiment Analysis.
        """
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(content)

        sentiment_details = {
            "positive": scores['pos'],
            "neutral": scores['neu'],
            "negative": scores['neg'],
            "compound": scores['compound']
        }

        # Determine sentiment based on compound score
        if scores['compound'] >= 0.05:
            return "positive", sentiment_details
        elif scores['compound'] <= -0.05:
            return "negative", sentiment_details
        else:
            return "neutral", sentiment_details

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])  # Allow public access
    def stats(self, request):
        """
        Provide statistics for the admin dashboard.
        """
        total_feedback = Feedback.objects.count()
        pending_review = Feedback.objects.filter(admin_response__isnull=True).count()
        reviewed = Feedback.objects.filter(admin_response__isnull=False).count()

        stats = {
            "total_feedback": total_feedback,
            "pending_review": pending_review,
            "reviewed": reviewed,
        }
        return Response(stats)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def mark_reviewed(self, request, pk=None):
        """
        Mark a feedback as reviewed.
        """
        feedback = self.get_object()
        feedback.admin_response = "Reviewed"
        feedback.save()
        return Response({"message": "Feedback marked as reviewed."})

    def get_queryset(self):
        """
        Override default queryset to add filters for room, sentiment, and date range.
        """
        queryset = super().get_queryset()

        # Filters
        room = self.request.query_params.get('room')
        sentiment = self.request.query_params.get('sentiment')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # Room filter
        if room:
            queryset = queryset.filter(room__name__icontains=room)

        # Sentiment filter
        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)

        # Date filter
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=[start_date, end_date])

        return queryset


class FeedbackReportView(APIView):
    """
    APIView to generate feedback analytics report for admins as a downloadable CSV file.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Generate a CSV report containing all feedback data.
        """
        # Set up the HTTP response for CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="feedback_report.csv"'

        # Create a CSV writer
        writer = csv.writer(response)

        # Write the header row
        writer.writerow([
            "ID",
            "User",
            "Full Name",
            "Field of Study",
            "Room",
            "Student ID",
            "Content",
            "Rating",
            "Sentiment",
            "Admin Response",
            "Created At"
        ])

        # Query all feedback and write to CSV
        feedbacks = Feedback.objects.all()
        for feedback in feedbacks:
            writer.writerow([
                feedback.id,
                feedback.user.username if feedback.user else "Anonymous",
                feedback.full_name,
                feedback.field_of_study,
                feedback.room.name if feedback.room else "N/A",
                feedback.student_id,
                feedback.content,
                feedback.rating,
                feedback.sentiment,
                feedback.admin_response or "Pending Review",
                feedback.created_at,
            ])

        return response