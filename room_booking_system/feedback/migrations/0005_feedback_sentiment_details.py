# Generated by Django 5.1.4 on 2025-01-19 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0004_feedback_field_of_study_feedback_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='sentiment_details',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
