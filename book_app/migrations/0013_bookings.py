# Generated by Django 5.1.6 on 2025-02-15 13:59

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0012_backupbooking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('team1_name', models.CharField(max_length=100)),
                ('team2_name', models.CharField(blank=True, max_length=100, null=True)),
                ('mobile_number_team1', models.CharField(max_length=15)),
                ('mobile_number_team2', models.CharField(blank=True, max_length=15, null=True)),
                ('email_team1', models.EmailField(max_length=254)),
                ('email_team2', models.EmailField(blank=True, max_length=254, null=True)),
                ('date', models.DateTimeField()),
                ('time_slot', models.CharField(max_length=20)),
                ('total_cost', models.IntegerField()),
                ('cost_per_team', models.IntegerField(blank=True, null=True)),
                ('payment_status_team1', models.BooleanField(default=False)),
                ('payment_status_team2', models.BooleanField(default=False)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('ground', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_app.ground')),
            ],
        ),
    ]
