# Generated by Django 5.1.4 on 2025-01-18 08:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_feedback_admin_response_feedback_sentiment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='admin_response',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='rating',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='sentiment',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
