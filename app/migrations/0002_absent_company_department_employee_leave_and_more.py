# Generated by Django 4.1.7 on 2023-12-13 04:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Absent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('absent_on', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('email', models.EmailField(max_length=500, unique=True)),
                ('website', models.CharField(max_length=500)),
                ('telephone', models.CharField(max_length=500)),
                ('telephone1', models.CharField(blank=True, max_length=500, null=True)),
                ('telephone2', models.CharField(blank=True, max_length=500, null=True)),
                ('address', models.CharField(max_length=500)),
                ('pincode', models.CharField(max_length=500)),
                ('city', models.CharField(max_length=500)),
                ('state', models.CharField(max_length=500)),
                ('country', models.CharField(max_length=500)),
                ('branch', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dep_code', models.CharField(max_length=50)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emp_id', models.CharField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('company_contact', models.CharField(blank=True, max_length=100, null=True)),
                ('personal_contact', models.CharField(max_length=100)),
                ('present_address', models.CharField(blank=True, max_length=100, null=True)),
                ('permanent_address', models.CharField(blank=True, max_length=100, null=True)),
                ('dob', models.DateField()),
                ('doj', models.DateField()),
                ('gender', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=70, null=True)),
                ('office_email', models.EmailField(max_length=70)),
                ('image', models.ImageField(default='user.png', upload_to='images/')),
                ('status', models.BooleanField(default=True)),
                ('designation', models.CharField(max_length=200)),
                ('level', models.CharField(max_length=100)),
                ('deactivate', models.CharField(blank=True, max_length=5000, null=True)),
                ('activate', models.CharField(blank=True, max_length=5000, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.department')),
                ('reporting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.employee')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('days', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='LeaveApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apply_on', models.DateField(auto_now=True)),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('reason', models.CharField(blank=True, max_length=250)),
                ('leave_count', models.IntegerField(blank=True, null=True)),
                ('level1_reject', models.BooleanField(default=False)),
                ('level1_approve', models.BooleanField(default=False)),
                ('level1_comm', models.CharField(blank=True, max_length=100)),
                ('level2_reject', models.BooleanField(default=False)),
                ('level2_approve', models.BooleanField(default=False)),
                ('level2_comm', models.CharField(blank=True, max_length=100)),
                ('status_reject', models.BooleanField(default=False)),
                ('status_approve', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.leave')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LeavePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leavepolicy', models.CharField(max_length=50000)),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotes', models.TextField(max_length=300)),
                ('tod_date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Absent_emp',
        ),
        migrations.DeleteModel(
            name='Addemployee',
        ),
        migrations.DeleteModel(
            name='Admin_Login',
        ),
        migrations.DeleteModel(
            name='CompanySetup',
        ),
        migrations.DeleteModel(
            name='Leave_App',
        ),
        migrations.DeleteModel(
            name='Leave_Policy',
        ),
        migrations.AddField(
            model_name='event',
            name='visibility',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('Birthday', 'Birthday'), ('Public Holiday', 'Public Holiday'), ('Event', 'Event'), ('Others', 'Others')], max_length=20),
        ),
        migrations.AddField(
            model_name='absent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.employee'),
        ),
    ]
