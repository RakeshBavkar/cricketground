# Generated by Django 5.1.5 on 2025-01-16 08:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Court',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('court_name', models.CharField(max_length=50)),
                ('court_name_postfix', models.CharField(blank=True, max_length=10, null=True)),
                ('created_at', models.DateField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_time', models.TimeField()),
                ('to_time', models.TimeField()),
                ('is_booked', models.BooleanField(default=False)),
                ('booking_time', models.DateTimeField(blank=True, null=True)),
                ('on_hold', models.BooleanField(default=False)),
                ('hold_start_time', models.DateTimeField(blank=True, null=True)),
                ('team1_name', models.CharField(blank=True, max_length=20, null=True)),
                ('team2_name', models.CharField(blank=True, max_length=20, null=True)),
                ('booked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booked_by', to=settings.AUTH_USER_MODEL)),
                ('court', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='booking_app.court')),
                ('hold_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hold_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
