# Generated by Django 4.1.7 on 2023-12-13 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_employee_com_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='com_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.company'),
        ),
        migrations.AddField(
            model_name='quote',
            name='com_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.company'),
        ),
    ]
