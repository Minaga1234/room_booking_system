# Generated by Django 4.2.11 on 2025-01-28 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('booking_update', 'Booking Update'), ('penalty_reminder', 'Penalty Reminder'), ('general', 'General'), ('admin_alert', 'Admin Alert')], default='general', max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookings.booking')),
            ],
        ),
    ]
