# Generated by Django 5.1.6 on 2025-02-11 14:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0005_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
