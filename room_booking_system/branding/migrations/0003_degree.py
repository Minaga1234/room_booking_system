# Generated by Django 5.1.4 on 2024-12-31 08:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('branding', '0002_alter_branding_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the degree', max_length=255)),
                ('branding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='degrees', to='branding.branding')),
            ],
        ),
    ]
