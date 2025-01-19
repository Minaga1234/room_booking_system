from django.contrib import admin
from .models import Feedback
from django.db.models import Count, Avg

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'field_of_study', 'room', 'student_id', 'rating', 'sentiment', 'created_at')
    list_filter = ('field_of_study', 'sentiment', 'created_at')
    search_fields = ('full_name', 'student_id', 'content')

    def changelist_view(self, request, extra_context=None):
        # Add custom data to admin view
        total_feedback = Feedback.objects.count()
        average_rating = Feedback.objects.aggregate(Avg('rating'))['rating__avg']
        sentiment_distribution = Feedback.objects.values('sentiment').annotate(count=Count('sentiment'))

        extra_context = extra_context or {}
        extra_context['total_feedback'] = total_feedback
        extra_context['average_rating'] = average_rating
        extra_context['sentiment_distribution'] = sentiment_distribution
        return super().changelist_view(request, extra_context=extra_context)