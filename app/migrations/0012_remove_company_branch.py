# Generated by Django 4.1.7 on 2023-12-18 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_leaveapplication_level0_approve_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='branch',
        ),
    ]
