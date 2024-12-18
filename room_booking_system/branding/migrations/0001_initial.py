# Generated by Django 5.1.4 on 2024-12-18 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Branding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=100)),
                ('logo_path', models.ImageField(blank=True, null=True, upload_to='branding/logos/')),
                ('favicon_path', models.ImageField(blank=True, null=True, upload_to='branding/favicons/')),
                ('cover_photo_path', models.ImageField(blank=True, null=True, upload_to='branding/covers/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
