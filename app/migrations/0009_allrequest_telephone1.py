# Generated by Django 4.1.7 on 2023-12-14 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_leave_com_id_leavepolicy_com_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='allrequest',
            name='telephone1',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
