from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from datetime import datetime, date, timedelta
import calendar, math
import string, random, time
import pandas as pd
from openpyxl import Workbook
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from .utils import Calendar, Eventcal 
from django.utils.safestring import mark_safe 
from django.views import generic
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q, Count, Sum
from .helper import send_account_creation_mail, send_company_login_credential_mail, send_admin_forgot_password_otp, send_mail_about_client_request, send_otp_for_email_verification
import json
import os
import io
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import landscape, A4, A1, A2, A3
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import send_mail
from django.core.management import call_command
from cryptography.fernet import Fernet, InvalidToken
import zipfile
import json, urllib.request, requests
from django.conf import settings
import uuid

from django.contrib.auth.models import User

from datetime import datetime, date, timedelta

from django.utils import timezone




# Check is admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

# Check is HR Admin
def is_hr(user):
    return user.groups.filter(name='HR').exists()

# Check is employee
def is_employee(user):
    return user.groups.filter(name='EMPLOYEE').exists()

# Index Page
def landingpage(request):
    return render(request,"landingPage.html")

# Home Page
def homepage(request):
    return render(request,"homePage.html")

# Request LEAPSS app
def requestApplication(request):
    if request.method == 'POST':
        form = AppRequestForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)            
            # instance.active_status = True
            # instance.username = instance.email
            # request.session['app_request_data'] = form.cleaned_data
            otp = str(random.randint(100000, 999999))
            request.session['app_request_data'] = {
                'form_data': form.cleaned_data,
                'otp': otp
            }
            send_otp_for_email_verification(otp, instance.email)
            return redirect('email_verification')
        else:
            if 'company_name' in form.errors:
                messages.error(request, 'Company Name already exists.')
            if 'website' in form.errors:
                messages.error(request, 'Website with this address already exists.')
            if 'email' in form.errors:
                messages.error(request, 'Email already exists.')
            if 'telephone' in form.errors:
                messages.error(request, 'Phone number already exists.')
    else:
        form = AppRequestForm()

    context ={
        'form':form
    }
    return render(request, 'applyApplication.html', context)

def emailVerification(request):
    if 'app_request_data' not in request.session:
        return HttpResponse("No application data found in session.")

    if request.method == 'POST':
        verification_code = request.POST['verification_code']
        app_data = request.session['app_request_data']
        generated_otp = app_data.get('otp')
        if verification_code == generated_otp:
            form_data = app_data.get('form_data')
            # instance = get_object_or_404(AllRequest, email=form_data['email'])
            # instance.active_status = True
            # instance.username = instance.email
            # instance.save()
            instance = AllRequest.objects.create (
                company_name=form_data['company_name'],
                website=form_data['website'],
                email=form_data['email'],
                telephone=form_data['telephone'],
                telephone1=form_data['telephone1'],
                country=form_data['country'],
                state=form_data['state'],
                city=form_data['city'],
                address=form_data['address'],
                pincode=form_data['pincode'],
                active_status=True,
                username=form_data['email'] 
            )
            send_mail_about_client_request(instance.company_name)
            del request.session['app_request_data']
            return render(request, 'successfullyApply.html')

    return render(request, 'emailVerification.html')

def successfullyApply(request):
    return render(request, 'successfullyApply.html')

def appDisabled(request):
    return render(request, 'appDisabled.html')

def appRequestDashboard(request):
    clients = AllRequest.objects.filter(approve_status=False,decline_status=False).all()
    context ={
        'clients':clients
    }
    return render(request, 'appRequestDashboard.html', context)

def homeDashboard(request):
    client_id = request.GET.get('client_id', None)
    all_clients = AllRequest.objects.all()
    total_company = all_clients.count()

    approved_clients = AllRequest.objects.filter(active_status=True).count()
    inactive_clients = AllRequest.objects.filter(active_status=False).count()
    rejected_clients = AllRequest.objects.filter(decline_status=True).count()
    client_requests  = AllRequest.objects.filter(approve_status=False,decline_status=False).count()

    
    all_employee = None
    total_employee = 0
    in_activate = 0
    in_deactivate = 0

    if client_id is not None:
        
        all_employee = Employee.objects.filter(com_id=client_id)
        total_employee = all_employee.count()

        in_activate = Employee.objects.filter(com_id=client_id, status=True).count()
        in_deactivate = Employee.objects.filter(com_id=client_id, status=False).count()

    context = {
        'total_company': total_company,
        'approved_clients': approved_clients,
        'inactive_clients': inactive_clients,
        'rejected_clients': rejected_clients,
        'client_requests': client_requests,
        'all_clients': all_clients,
        'all_employee': all_employee,
        'total_employee': total_employee,
        'in_activate': in_activate,
        'in_deactivate': in_deactivate,
    }
    return render(request, 'homeDashboard.html', context)

def getDashboardData(request, client_id):
    try:
        all_employee = Employee.objects.filter(com_id=client_id)
        total_employee = all_employee.count()

        in_activate = Employee.objects.filter(com_id=client_id, status=True).count()
        in_deactivate = Employee.objects.filter(com_id=client_id, status=False).count()


        all_employee_list = json.loads(serialize('json', all_employee))

        data = {
            'all_employee': all_employee_list,
            'total_employee': total_employee,
            'in_activate': in_activate,
            'in_deactivate': in_deactivate,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})

def approvedClientDashboard(request):
    clients = AllRequest.objects.filter(approve_status=True).all().order_by('company_name')
    context ={
        'clients':clients,
        'page': "approvedClient"
    }
    return render(request, 'approvedClientDashboard.html', context)

def inactiveClientDashboard(request):
    clients = AllRequest.objects.filter(active_status=False, approve_status=True).all()
    context ={
        'clients':clients,
        'page': 'inactiveClient'
    }
    return render(request, 'approvedClientDashboard.html', context)

def activeClientDashboard(request):
    clients = AllRequest.objects.filter(active_status=True, approve_status=True).all()
    context ={
        'clients':clients,
        'page': 'activeClient'
    }
    return render(request, 'approvedClientDashboard.html', context)

def rejectedClientDashboard(request):
    clients = AllRequest.objects.filter(decline_status=True).all()
    context ={
        'clients':clients
    }
    return render(request, 'rejectedClientDashboard.html', context)

def ApproveClient(request, client_id):
    client = AllRequest.objects.filter(pk=client_id).first()
    client.approve_status = True
    client.save()
    characters = string.ascii_letters + string.digits + string.punctuation
    custom_password = ''.join(random.choice(characters) for _ in range(10))
    company = Company()
    company.name = client.company_name
    company.website = client.website
    company.email = client.email
    company.telephone = client.telephone
    company.telephone1 = client.telephone1
    company.city = client.city
    company.state = client.state
    company.country = client.country
    company.address = client.address
    company.pincode = client.pincode
    company.username = client.username
    company.password = custom_password
    company.setup_completed = False
    company.save()
    send_company_login_credential_mail(client.company_name, client.username, custom_password)
    return redirect('appRequestDashboard')

def RejectClient(request, client_id):
    client = AllRequest.objects.filter(pk=client_id).first()
    client.decline_status = True
    client.save()
    return redirect('appRequestDashboard')

def undoClient(request, client_id):
    client = AllRequest.objects.filter(pk=client_id).first()
    client.decline_status = False
    client.save()
    return redirect('rejectedClientDashboard')

def enableClient(request, client_id):
    client = AllRequest.objects.filter(pk=client_id).first()
    client.active_status = True
    client.save()
    return redirect('approvedClientDashboard')

def disableClient(request, client_id):
    client = AllRequest.objects.filter(pk=client_id).first()
    client.active_status = False
    client.save()
    return redirect('approvedClientDashboard')

def viewClient(request, client_id):
    client = AllRequest.objects.filter(pk=client_id).first()
    com = Company.objects.filter(email=client.email).first()
    context ={
        'com':com, 'client':client
    }
    return render(request, 'viewClient.html', context)

def companyLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            client = AllRequest.objects.get(username=username)
            if client.active_status == True:
                company = Company.objects.get(username=username,password=password)
                request.session['company_id'] = company.id
                if company.setup_completed == True:
                    user = authenticate(username=username, password=password)
                    if user:
                        if user.groups.filter(name='ADMIN'):
                            auth_login(request,user)
                            return redirect('adminDashboard')
                        else:
                            messages.success(request, 'Your account is not found')
                    else:
                        messages.success(request, 'Check your username and password')
                else:
                    otp = str(random.randint(100000, 999999))
                    send_admin_forgot_password_otp(otp, company.email)
                    return redirect('newCompanySetup',otp=otp, username=username)
            else:
                return redirect('appDisabled')
        except Company.DoesNotExist:
            user = authenticate(username=username, password=password)
            if user:
                if user.groups.filter(name='ADMIN'):
                    auth_login(request,user)
                    return redirect('adminDashboard')
                else:
                    messages.success(request, 'Your account is not found')
            else:
                messages.success(request, 'Check your username and password')
            messages.error(request, 'Invalid credentials')
        except AllRequest.DoesNotExist:
            messages.error(request, 'Company Not Found')
    return render(request, 'companyLogin.html')

def newCompanySetup(request, otp, username):
    if request.method == 'POST':
        old_password = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        confirm_password = request.POST['confirmPassword']
        if new_password == confirm_password:
            if old_password == otp:
                try:
                    company = Company.objects.get(username=username)
                    company.password = new_password
                    company.save()

                    # Creating Admin for the Company
                    if not User.objects.filter(username=username).exists():
                        # Creating superuser
                        new_superuser = User.objects.create_superuser(username, company.email, new_password)
                        
                        # Adding superuser to Admin group
                        admin_group, created = Group.objects.get_or_create(name='ADMIN')
                        new_superuser.groups.add(admin_group)
                        
                        # Assigning all available permissions to the superuser
                        permissions = Permission.objects.all()
                        for permission in permissions:
                            new_superuser.user_permissions.add(permission)
                        
                        company.setup_completed = True
                        company.save()

                        # Creating dummy departments
                        Department.objects.create(
                            department='Production',
                            dep_code='001',
                            com_id=company
                        )
                        Department.objects.create(
                            department='IT',
                            dep_code='002',
                            com_id=company
                        )
                        Department.objects.create(
                            department='Finance',
                            dep_code='003',
                            com_id=company
                        )
                        Department.objects.create(
                            department='Marketing',
                            dep_code='004',
                            com_id=company
                        )

                        # Creating dummy Leave Baskets
                        Leave.objects.create(
                            name='Sick Leave',
                            days=15,
                            com_id=company
                        )
                        Leave.objects.create(
                            name='Paid Leave',
                            days=30,
                            com_id=company
                        )

                        # Creating dummy Privacy Policy
                        PrivacyPolicy.objects.create(
                            privacypolicy=f'<p>Privacy Policy of</p><h2>{company.name}</h2>',
                            com_id=company
                        )

                        #Creating dummy Terms and Conditions
                        Terms.objects.create(
                            terms=f'<p>Terms and Conditions of</p><h2>{company.name}</h2>',
                            com_id=company
                        )

                        #Creating dummy Leave Policy
                        LeavePolicy.objects.create(
                            leavepolicy=f'<p>Leave Policy Of of</p><h2>{company.name}</h2>',
                            com_id=company
                        )

                        response = redirect('homepage')
                        response.set_cookie('company_id', company.id)
                        return response
                    else:
                        messages.warning(request, 'Superuser already exists')
                except Company.DoesNotExist:
                    messages.error(request, 'Email not found or incorrect password')
            else:
                 messages.error(request, 'Invalid OTP')
        else:
            messages.error(request, 'Password and confirm password must be the same')

    return render(request, 'newCompanySetup.html')

def adminForgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            valid_email = User.objects.get(username=email).username
            otp = str(random.randint(100000, 999999))
            send_admin_forgot_password_otp(otp, email)
            return redirect('changeAdminPassword', otp=otp , email=valid_email)
        except User.DoesNotExist:
            messages.error(request, 'Email was not found')
    return render(request, 'forgotPassword.html')

def changeAdminPassword(request, otp, email):
    if request.method == 'POST':
        user_otp = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        confirm_password = request.POST['confirmPassword']
        if new_password == confirm_password:
            if otp == user_otp:
                try:                                                                                            
                    user = User.objects.get(username=email)
                    user.set_password(new_password)
                    user.save()
                    return redirect('homepage')
                except Exception as e:
                    print(f"An exception occurred: {e}")
            else:
                messages.error(request, 'Invalid OTP')
        else:
            messages.error(request, 'Password and confirm password must be the same')
    return render(request, 'newCompanySetup.html')

# Admin Login Page 
# def adminLogin(request):
#     if request.method == 'POST':
#         form = AdminLoginForm(request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = authenticate(username=username, password=password)
#             if user:
#                 if user.groups.filter(name='ADMIN'):
#                     auth_login(request,user)
#                     return redirect('adminDashboard')
#                 else:
#                     messages.success(request, 'Your account is not found')
#             else:
#                 messages.success(request, 'Check your username and password')
#     else:
#          form = AdminLoginForm()

#     context ={
#         'form':form
#     }
#     return render(request, 'adminLogin.html', context)

# Admin logout
def logout_view(request):
    logout(request)
    return redirect('/')

# Admin dashboard
class CalendarView(generic.ListView):
    model = Event
    template_name = 'adminDashboard.html'

    @method_decorator(login_required(login_url='adminLogin'))
    @method_decorator(user_passes_test(lambda u: is_admin(u) or is_hr(u)))
    def dispatch(self, *args, **kwargs):
        return super(CalendarView, self).dispatch(*args, **kwargs)
    
    def dash(self):
        com = Company.objects.filter(username=self.request.user.username).first()
        is_employee = False
        if com is None:
            emp = Employee.objects.filter(office_email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
            is_employee = True
        emails = Employee.objects.filter(com_id=com).values_list('office_email', flat=True)
        today = datetime.today().strftime("%Y-%m-%d")
        total_emp = Employee.objects.filter(status=True, com_id = com).count()
        onleave = LeaveApplication.objects.filter(user__employee__status=True,status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails).count()
        absent_count = Absent.objects.filter(absent_on = today).count()
        present_today = total_emp - (onleave + absent_count)
        total_leave = onleave + absent_count
        apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True, user__username__in=emails).count()

        dic ={'com':com, 'total_emp':total_emp, 'present_today':present_today, 'onleave':onleave, 'total_leave':total_leave, 'apply_leav':apply_leav, 'is_employee':is_employee}       
        return dic 
    
    def quotesub(self): 
        com = Company.objects.filter(username=self.request.user.username).first()
        if com is None:
            emp = Employee.objects.filter(office_email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
        quote = Quote.objects.all().last() 
        form = QuoteForm()
        # if quote is None:
        if self.request.method == "GET": 
            form = QuoteForm(self.request.GET)
            if form.is_valid():
                data = form.save(commit=False)
                data.com_id=com
                data.save()
                return redirect('adminDashboard')   
        else:
            form = QuoteForm()
        # else:
        #     instance = Quote.objects.filter(com_id = com).last()
        #     form = QuoteUpdateForm(self.request.GET or None, instance=instance)
        #     if form.is_valid():
        #         form.save()
        quotes = {'quote':quote,'form':form}
        return quotes

    def quote(self):
    
        com = Company.objects.filter(username=self.request.user.username).first()
        if com is None:
            emp = Employee.objects.filter(office_email=self.request.user.username).first()
            com = get_object_or_404(Company, name=emp.com_id)

        try:
           
            quotedd = Quote.objects.filter(com_id=com).order_by('-id').first()
            quoted_name = quotedd.quotes if quotedd else None
        except Quote.DoesNotExist:
            quoted_name = None

        return quoted_name
       
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        com = Company.objects.filter(username=self.request.user.username).first()
        queries = Support.objects.filter(company_id=com)
        if com is None:
            print(self.request.user.username)
            emp = Employee.objects.filter(office_email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
        # use today's date for the calendar
        adminStatus = True
        today = str(get_date(self.request.GET.get('day', None)))
        today_year, today_month, today_date = (int(x) for x in today.split('-'))
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['queries'] = queries
        context['next_month'] = next_month(d)
        cal = Calendar(d.year, d.month, today_date, today_month, today_year, adminStatus)
        html_cal = cal.formatmonth(com, withyear=True)
        context['calendar'] = mark_safe(html_cal)
        event = Eventcal(d.year, d.month, adminStatus)
        html_event = event.formatmonth(com, withyear=True)
        context['event'] = mark_safe(html_event)
        context['dic']=self.dash()
        context['quotes'] = self.quotesub()  
        context['quote'] = self.quote()
        context['quote_history'] = Quote.objects.filter(com_id = com).order_by('-id').all()
        return context

# Total Employee
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def totalEmployees(request): 
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
            emp = Employee.objects.filter(office_email=request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
    emails = Employee.objects.filter(com_id=com).values_list('email', flat=True)
    today = datetime.today().strftime("%Y-%m-%d")
    total_emp = Employee.objects.filter(status=True, com_id = com).count()
    onleave = LeaveApplication.objects.filter(user__employee__status=True,status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails).count()
    absent_count = Absent.objects.filter(absent_on = today, user__user__username__in=emails).count()
    present_today = total_emp - (onleave + absent_count)
    dep_count = Employee.objects.values('department__department','department').filter(status=True, com_id = com).annotate(emp_count=Count('emp_id'))
    total_leave = onleave + absent_count
    apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True).count()
    context = {'total_emp':total_emp, 'dep_count':dep_count, 'present_today':present_today, 'onleave':onleave, 'total_leave':total_leave,'apply_leav':apply_leav, 'com':com }
    return render(request,'totalEmployees.html', context)

# Total Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def totalEmployeeDetails(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
            emp = Employee.objects.filter(office_email=request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
    emails = Employee.objects.filter(com_id=com).values_list('email', flat=True)
    total_emp = Employee.objects.filter(status=True, com_id = com).count()
    dep = Department.objects.get(id=id)
    emp = Employee.objects.filter(department=id,status = True)
    today = datetime.today().strftime("%Y-%m-%d")
    total_emp = Employee.objects.filter(status=True, com_id = com).count()
    onleave = LeaveApplication.objects.filter(user__employee__status=True, status_approve=True, date_from__lte=today, date_to__gte=today).count()
    absent_count = Absent.objects.filter(absent_on = today, user__user__username__in=emails).count()
    present_today = total_emp - (onleave + absent_count)
    total_leave = onleave + absent_count
    apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True).count()
    context = {'total_emp':total_emp, 'dep':dep, 'emp':emp, 'present_today':present_today, 'onleave':onleave, 'total_leave':total_leave,'apply_leav':apply_leav }
    return render(request,'totalEmployeeDetails.html', context)


# Prest employee Page
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def presentEmployees(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
            emp = Employee.objects.filter(office_email=request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
    emails = Employee.objects.filter(com_id=com).values_list('office_email', flat=True)
    today = datetime.today().strftime("%Y-%m-%d")
    total_emp = Employee.objects.filter(status=True, com_id = com).count()
    onleave = LeaveApplication.objects.filter(user__employee__status=True, status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails).count()
    absent_count = Absent.objects.filter(absent_on = today, user__user__username__in=emails).count()
    present_today = total_emp - (onleave + absent_count)
    total_leave = onleave + absent_count 
    apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True).count()
    
    leave = LeaveApplication.objects.filter(status_approve=True, date_from__lte=today, date_to__gte=today).values('user__id')
    absent = Absent.objects.filter(absent_on=today, user__user__username__in=emails).values('user__user__id')
    present = Employee.objects.filter(user__username__in=emails,status=True ).exclude(Q(user__id__in = absent) | Q(user__id__in = leave))
    context = {'total_emp':total_emp, 'present_today':present_today, 'onleave':onleave, 'total_leave':total_leave, 'apply_leav':apply_leav, 'present':present, 'com':com}
    return render(request,'presentEmployees.html', context)


# On leave page
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def onLeave(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emails = Employee.objects.filter(com_id=com).values_list('email', flat=True)
    today = datetime.today().strftime("%Y-%m-%d")
    total_emp = Employee.objects.filter(status=True, com_id = com).count()
    leav = LeaveApplication.objects.filter(user__employee__status=True, status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails)
    onleave = LeaveApplication.objects.filter(user__employee__status=True, status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails).count()
    absent = Absent.objects.filter(absent_on = today, user__user__username__in=emails)
    absent_count = Absent.objects.filter(absent_on = today, user__user__username__in=emails).count()
    present_today = total_emp - (onleave + absent_count)
    total_leave = onleave + absent_count
    apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True).count()
    if request.method == "POST":
        form = AbsentForm(request.POST, com_id=com.id)
        if form.is_valid():
            user=form.save()
            user.save()
            return HttpResponseRedirect(request.path_info)
    form = AbsentForm(com_id=com.id)
    context = {'total_emp':total_emp, 'present_today':present_today, 'onleave':onleave, 'leav':leav, 'form':form, 'absent':absent, 'absent_count':absent_count, 'total_leave':total_leave,'apply_leav':apply_leav,'com':com}
    return render(request,'onLeave.html', context)

# Delete Absent
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def deleteAbsent(request, id):
    abs = Absent.objects.get(id=id)
    abs.delete()
    return redirect(reverse('onLeave'))

# Active Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def activeEmployee(request): 
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter(status=True, com_id=com).order_by('name')
    context = {'emp':emp,'com':com}
    return render(request, 'activeEmployee.html', context)


#All Active Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def allactiveEmployee(request): 
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter( com_id=com).order_by('name')
    context = {'emp':emp,'com':com,  'status': 'Active'}
    return render(request, 'allactiveEmployee.html', context)


# Deactivate detail employee page 
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def deactivateDetail(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.get(id=id)
    form = DeactivateForm()
    if request.method == 'POST':
        form = DeactivateForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            emp.status=False
            emp.save()
            return redirect(reverse('activeEmployee'))
    else:
        form=DeactivateForm()
    context = {'form':form, 'com':com, 'client': emp}
    return render(request, 'deactivate.html', context)

# Inactive Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def inactiveEmployee(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter(status=False, com_id=com)
    context = {'emp':emp,'com':com}
    return render(request, 'inactiveEmployee.html', context)

# Deactivate detail employee page 
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def activateDetail(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.get(id=id)
    form = ActivateForm()
    if request.method == 'POST':
        form = ActivateForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            emp.status=True
            emp.save()
            return redirect(reverse('activeEmployee'))
    else:
        form=ActivateForm()
    context = {'form':form, 'com':com, 'client': emp}
    return render(request, 'activate.html', context)

# Add Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def addEmployee(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter(level = 'Level 1' or 'Level 2')
    if request.method == "POST":

        form1 = AddEmployeeForm(request.POST, request.FILES, com_id=com.id)
        if form1.is_valid():
            characters = string.ascii_letters + string.digits + string.punctuation
            custom_password = ''.join(random.choice(characters) for _ in range(10))
            name = request.POST['name']
            office_email = request.POST['office_email']
            username = office_email
            password = custom_password
            company = com.name

            user=User.objects.create(username=username)
            user.set_password(password)
            user.save()

            f2=form1.save(commit=False)
            f2.user=user
            f2.com_id=com
            f2.employee_setup_completed=False
            user1=f2.save()

            

            send_account_creation_mail(office_email, name, company, username, password)
            group=Group.objects.get_or_create(name='EMPLOYEE')
            group[0].user_set.add(user)
            if f2.level == "Level 0":
                group=Group.objects.get_or_create(name='HR')
                group[0].user_set.add(user)
            return redirect('activeEmployee')
        else:
            print(form1.errors)
    else:
        form1 = AddEmployeeForm(com_id=com.id)
    context={'form1':form1, 'emp':emp,'com':com}
    return render(request, 'addEmployee.html', context)


def check_email_uniqueness(request):
    if request.method == 'POST' and request.is_ajax():
        email = request.POST.get('email', None)
        is_unique = not Employee.objects.filter(email=email).exists()
        return JsonResponse({'is_unique': is_unique})
    

# Upload Employee Detail through Excell
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def addEmployeebyExcel(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    if request.method == 'POST':
        file = request.FILES['file']  # Assuming you have a form field named 'file' for file upload
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
            
            for index, row in df.iterrows():
  
                # Extract data from the Excel columns
                emp_id = row['Employee ID']
                name = row['Name']
                company_contact = row['Company Contact']
                personal_contact = row['Personal Contact']
                present_address = row['Present Address']
                permanent_address = row['Permanent Address']
                dob = row['DOB']
                doj = row['DOJ']
                gender = row['Gender'] 
                email = row['Email']
                office_email = row['Office Email']
                designation = row['Designation']
                level = row['Level']
                department =  Department.objects.get(department=row['Department'],com_id = com)
                password = "12345678"
                # image = row['image']
                # Create a User instance
                user_instance = User.objects.create_user(username=office_email, password=password)
                
                # Create an Employee instance and link it to the User instance
                employee = Employee.objects.create(
                    user=user_instance,
                    emp_id=emp_id,
                    com_id=com,
                    name=name,
                    company_contact=company_contact,
                    personal_contact=personal_contact,
                    present_address=present_address,
                    permanent_address=permanent_address,
                    dob=dob,
                    doj=doj,
                    gender=gender,
                    email=email,
                    office_email=office_email,
                    # image=image,
                    status=True,
                    designation=designation,
                    level=level,
                    department=department
                )
                send_account_creation_mail(office_email, name, com, office_email, password)
                group=Group.objects.get_or_create(name='EMPLOYEE')
                group[0].user_set.add(user_instance)
                if level == "Level 0":
                    group=Group.objects.get_or_create(name='HR')
                    group[0].user_set.add(user_instance)
            return redirect("activeEmployee")
        else:
            return render(request, 'addEmployee.html')
        
# Download Employee Detail in Excell
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def download_employees_as_excel(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="Employees of {com}.xlsx"'

    # Create a workbook and add a worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"Employees of {com}"

    # Define column headers
    headers = [
        'Employee ID', 'Name', 'Company Contact', 'Personal Contact', 'Present Address',
        'Permanent Address', 'DOB', 'DOJ', 'Gender', 'Email', 'Office Email',
        'Status', 'Designation', 'Level', 'Department'
    ]
    ws.append(headers)

    # Retrieve data from Employee model and add it to the worksheet
    employees = Employee.objects.filter(com_id = com).all()
    for employee in employees:
        row = [
            employee.emp_id, employee.name, employee.company_contact, employee.personal_contact,
            employee.present_address, employee.permanent_address, employee.dob, employee.doj,
            employee.gender, employee.email, employee.office_email, employee.status,
            employee.designation, employee.level, employee.department.department
        ]
        ws.append(row)

    # Save the workbook to the response
    wb.save(response)
    return response

# View Employee Details
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def viewEmployee(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.get(id=id)
    context = {'emp':emp,'com':com}
    return render(request,'employeeProfile1.html', context) 

# Edit Employee Details
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def editEmployee(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    
    data = Employee.objects.get(id=id)
    instance = Employee.objects.get(pk=id)
    # userdata = User.objects.get(id=id)
    instance1 = User.objects.get(pk=instance.user.id)
    form = EmployeeUpdateForm(request.POST or None, request.FILES or None, instance=instance, com_id=com.id)

    if form.is_valid():
        official_email = request.POST.get('office_email')
        level = request.POST.get('level')
        
        if level == "Level 0":
            # Ensure that 'HR' group exists
            group, created = Group.objects.get_or_create(name='HR')
            # Add the user to the 'HR' group
            group.user_set.add(instance1)
        
        instance1.username = official_email
        instance1.save()
        form.save()

        messages.success(request, 'Details have been updated.')
        return redirect('activeEmployee')

    context = {'form': form, 'data': data, 'com': com}
    return render(request, 'editEmployee.html', context)

# Admin Change password of Employee
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def changePassword(request, id):
    emp = Employee.objects.get(id=id)
    user = User.objects.get(id=emp.user.id)
    form = SetPasswordForm(user=user, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('activeEmployee')
    context = {'form': form}
    return render(request, 'changePassword.html', context)



# Company setup
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def companySetup(request):
    form = CompanySetupForm()
    com = Company.objects.filter(username=request.user.username).first()
    is_employee = False
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
        is_employee = True
    if request.method == "POST": 
        form = CompanySetupForm(request.POST)
        if form.is_valid():
            data = form.save()
            data.save()
            return redirect('addDepartment')   
    else:
        form = CompanySetupForm()
    context = {'form':form, 'com':com, 'is_employee':is_employee}
    return render(request,'companySetup.html', context)

# Edit company
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def editCompany(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    com = get_object_or_404(Company, username=request.user.username)
    
    if request.method == 'POST':
        form = CompanyUpdateForm2(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('companySetup')
    else:
        form = CompanyUpdateForm2(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'com': com,
    }
    return render(request, 'editCompany.html', context)

# Department
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def department(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    dep = Department.objects.filter(com_id=com).all()
    context = {'dep':dep, 'com':com}
    return render(request, 'department.html', context)

# Add Department
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def addDepartment(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    if request.method == "POST":
        form = CompanyDepForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.com_id=com 
            data.save()
            return redirect('department')
        else:
            print("Form Errors:", form.errors)
    else:
        form = CompanyDepForm(initial={'com_id': com.id if com else None})
        form.fields['com_id'].widget = forms.HiddenInput()
    context={'form':form, 'com':com}
    return render(request, 'addDepartment.html', context)

# Edit Department
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def editDepartment(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    instance = Department.objects.get(pk=id)
    form = CompanyDepUpdateForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('department')

    context = {'form':form, 'com':com}
    return render(request, 'editDepartment.html', context)

# Delete Department 
@login_required(login_url='adminLogin') 
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def deleteDepartment(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    list =[]
    dep = Department.objects.get(id=id)
    dep_count = Employee.objects.values('department__department','department').filter(status=True, com_id = com).annotate(emp_count=Count('emp_id'))
    for dept in dep_count:
        list.append(dept['department__department'])
    if dep.department in list: 
        messages.success(request, 'There are employees in the department.')   
        return redirect('department')
    else: 
        dep.delete()
        messages.success(request, 'Departmet is Deleted.') 
        return redirect('department')

# Leave Policy Setting
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def leavePolicySetting(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    leave = LeavePolicy.objects.filter(com_id=com).first()
    count = Leave.objects.filter(com_id=com).count()
    l1 = math.ceil(count / 2)
    lea1 = Leave.objects.filter(com_id=com).order_by('-days')[:l1]
    lea2 = Leave.objects.filter(com_id=com).order_by('-days')[l1:]

    if leave is None:
        if request.method == "POST":
            form = LeavePolicyForm(request.POST, initial={'com_id': com.id})
            if form.is_valid():
                data = form.save(commit=False)
                data.com_id = com
                data.save()
                messages.success(request, "Privacy policy has been added.")
                return redirect('leavePolicySetting')
            else:
                messages.error(request, "form.errors")
                print(form.errors)
        else:
            form = LeavePolicyForm(initial={'com_id': com.id})
    else:
        instance = LeavePolicy.objects.get(pk=leave.id)
        print(instance)
        
        if request.method == "POST":

            form = LeavePolicyUpdateForm(request.POST or None, instance=instance, initial={'com_id': com.id})
            if form.is_valid():
                form.save()
                messages.success(request, "Leave policy is updated.")
                return redirect('leavePolicySetting')
            else:
                print(form.errors)
        else:
            form = LeavePolicyUpdateForm(instance=instance, initial={'com_id': com.id})

    context = {'leave': leave, 'form': form, 'lea1': lea1, 'lea2': lea2, 'com': com}
    return render(request, "leavePolicySetting.html", context)


# Privacy Policy Setting
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def setupPrivacyPolicy(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    privacy_details = PrivacyPolicy.objects.filter(com_id=com).first()
    if privacy_details is None:
        if request.method == "POST":
            form = PrivacyPolicyForm(request.POST, initial={'com_id': com.id})
            if form.is_valid():
                data = form.save(commit=False)
                data.com_id = com
                data.save()
                time.sleep(2)
                return redirect('companySetup')
            else:
                print(form.errors)
        else:
            form = PrivacyPolicyForm(initial={'com_id': com.id})
    else:
        instance = PrivacyPolicy.objects.get(com_id=com)
        form = PrivacyPolicyUpdateForm(request.POST or None, instance=instance, initial={'com_id': com.id})
        if request.method == "POST":
            if form.is_valid():
                form.save()
                time.sleep(2)
                return redirect('companySetup')
            else:
                print(form.errors)

    context = {'form': form, 'privacy_details': privacy_details, 'com': com}
    return render(request, "setupPrivacyPolicy.html", context)

# Terms & Conditions Setting
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def setupTandC(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    terms_details = Terms.objects.filter(com_id=com).first()
    if terms_details is None:
        if request.method == "POST":
            form = TermsForm(request.POST, initial={'com_id': com.id})
            if form.is_valid():
                data = form.save(commit=False)
                data.com_id = com
                data.save()
                time.sleep(2)
                return redirect('companySetup')
            else:
                print(form.errors)
        else:
            form = TermsForm(initial={'com_id': com.id})
    else:
        instance = Terms.objects.get(com_id=com)
        form = TermsUpdateForm(request.POST or None, instance=instance, initial={'com_id': com.id})
        if request.method == "POST":
            if form.is_valid():
                form.save()
                time.sleep(2)
                return redirect('companySetup')
            else:
                print(form.errors)

    context = {'form': form, 'terms_details': terms_details, 'com': com}
    return render(request, "setupTermsAndConditions.html", context)

# Add Leave
def addLeave(request):
    form = AddLeaveForm()
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    if request.method == 'POST':
        form = AddLeaveForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.com_id=com
            data.save()
            return redirect('leavePolicySetting')
        else:
            form = AddLeaveForm()
    context = {'form':form, 'com':com}
    return render(request, 'addLeave.html', context)

# Edit Leave
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def editLeave(request,id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    instance = Leave.objects.get(id=id)
    form = EditLeaveForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('leavePolicySetting')

    context = {'form':form, 'com':com, 'dep_id':id}
    return render(request,'editLeave.html', context)

# Delete Leave
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def deleteLeave(request,id):
    com = Company.objects.all().first()
    instance = Leave.objects.get(id=id)
    instance.delete()
    return redirect('leavePolicySetting')






def reportPrinting(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    form = PerticularEmployeeForm(request.POST or None, request.FILES or None, com_id=com.id)
    context = {'com':com, 'form':form}
    return render(request,'reportPrinting.html', context)

def download_pdf_report(request, option):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    # Create a PDF buffer and document object
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A3))

    # Create a list to hold table data
    data = [
        ['Employee ID', 'Name', 'Company Contact', 'Personal Contact', 'Present Address', 'Permanent Address',
         'Date of Birth', 'Date of Joining', 'Gender', 'Email', 'Office Email', 'Status', 'Designation', 'Level']
    ]

    # Create a sample stylesheet
    styles = getSampleStyleSheet()

    # Fetch employees based on the provided option
    if option == 'active':
        employees = Employee.objects.filter(com_id=com, status=True)
    elif option == 'inactive':
        employees = Employee.objects.filter(com_id=com, status=False)
    elif option == 'all':
        employees = Employee.objects.filter(com_id=com)

    # Iterate through employees
    for employee in employees:
        # Format data for each employee
        present_address = Paragraph(employee.present_address if employee.present_address else '', styles['Normal'])
        permanent_address = Paragraph(employee.permanent_address if employee.permanent_address else '', styles['Normal'])

        employee_data = [
            employee.emp_id,
            employee.name,
            employee.company_contact if employee.company_contact else '',
            employee.personal_contact,
            present_address,
            permanent_address,
            employee.dob.strftime('%Y-%m-%d') if employee.dob else '',
            employee.doj.strftime('%Y-%m-%d') if employee.doj else '',
            employee.gender,
            employee.email if employee.email else '',
            employee.office_email,
            'Active' if employee.status else 'Inactive',
            employee.designation,
            employee.level
        ]
        data.append(employee_data)

    # Create a table with styles
    style_table = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # ('PADDING', (0, 0), (-1, -1), 5),
    ]
    table = Table(data, style=style_table, repeatRows=1)

    # Create elements list and add the table
    elements = [table]

    # Build the PDF document with the elements list
    pdf.build(elements)

    # Get PDF content from BytesIO object
    pdf_bytes = buffer.getvalue()

    # Create a Django HttpResponse with PDF content as attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employee_report.pdf"'
    response.write(pdf_bytes)

    return response

def generate_employee_report(request):

    if request.method == 'POST':
        id = request.POST['employee']
        employee = Employee.objects.filter(id=id).first()
    else:
         form = EmployeeLoginForm()

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    # employee = Employee.objects.filter(id=id).first()

    if not employee:
        return HttpResponse("Employee not found", status=404)

    data = [
        ['Attribute', 'Value']
    ]

    employee_data = [
        ['Employee ID', employee.emp_id],
        ['Name', employee.name],
        ['Company Contact', employee.company_contact if employee.company_contact else ''],
        ['Personal Contact', employee.personal_contact],
        ['Present Address', employee.present_address if employee.present_address else ''],
        ['Permanent Address', employee.permanent_address if employee.permanent_address else ''],
        ['Date of Birth', employee.dob.strftime('%Y-%m-%d') if employee.dob else ''],
        ['Date of Joining', employee.doj.strftime('%Y-%m-%d') if employee.doj else ''],
        ['Gender', employee.gender],
        ['Email', employee.email if employee.email else ''],
        ['Office Email', employee.office_email],
        ['Status', 'Active' if employee.status else 'Inactive'],
        ['Designation', employee.designation],
        ['Department', employee.department],
        ['Reporting Person', employee.reporting],
        ['Level', employee.level]
    ]
    data.extend(employee_data)

    style_table = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 15),
    ])

    table = Table(data, style=style_table)
    elements = [table]

    pdf.build(elements)
    pdf_bytes = buffer.getvalue()

    # Create a Django HttpResponse with PDF content as attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="employee_report_{employee.id}.pdf"'
    response.write(pdf_bytes)

    return response

def download_event_report(request, option):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    # Create a PDF buffer and document object
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A3))

    # Create a list to hold table data
    data = [
        ['Title', 'Category', 'Description', 'Date']
    ]

    # Create a sample stylesheet
    styles = getSampleStyleSheet()

    # Fetch employees based on the provided option
    if option == 'all':
        events = Event.objects.filter(com_id=com)
    elif option == 'holiday':
        events = Event.objects.filter(com_id=com, category='Public Holiday')
    elif option == 'birthdayOthers':
        events = Event.objects.filter(com_id=com).exclude(category='Public Holiday')

    # Iterate through employees
    for event in events:
        event_data = [
            event.title,
            event.category,
            event.description,
            event.date.strftime('%Y-%m-%d') if event.date else '',
        ]
        data.append(event_data)

    # Create a table with styles
    style_table = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # ('PADDING', (0, 0), (-1, -1), 5),
    ]
    table = Table(data, style=style_table, repeatRows=1)

    # Create elements list and add the table
    elements = [table]

    # Build the PDF document with the elements list
    pdf.build(elements)

    # Get PDF content from BytesIO object
    pdf_bytes = buffer.getvalue()

    # Create a Django HttpResponse with PDF content as attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employee_report.pdf"'
    response.write(pdf_bytes)

    return response

def download_leave_report(request, option):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    # Create a PDF buffer and document object
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A3))

    # Create a list to hold table data
    data = [
        ['Employee ID', 'Name', 'Company Contact', 'Personal Contact',
         'Date of Birth', 'Date of Joining', 'Gender', 'Email', 'Office Email','Designation', 'Level']
    ]

    # Create a sample stylesheet
    styles = getSampleStyleSheet()

    # Fetch employees based on the provided option
    if option == 'present':
        emails = Employee.objects.filter(com_id=com).values_list('office_email', flat=True)
        today = datetime.today().strftime("%Y-%m-%d")    
        leave = LeaveApplication.objects.filter(status_approve=True, date_from__lte=today, date_to__gte=today).values('user__id')
        absent = Absent.objects.filter(absent_on=today, user__user__username__in=emails).values('user__user__id')
        employees = Employee.objects.filter(user__username__in=emails,status=True ).exclude(Q(user__id__in = absent) | Q(user__id__in = leave))
    elif option == 'absent':
        emails = Employee.objects.filter(com_id=com).values_list('office_email', flat=True)
        today = datetime.today().strftime("%Y-%m-%d")    
        leave = LeaveApplication.objects.filter(status_approve=True, date_from__lte=today, date_to__gte=today).values('user__id')
        absent = Absent.objects.filter(absent_on=today, user__user__username__in=emails).values('user__user__id')
        employees = Employee.objects.filter(user__username__in=emails, status=True).filter(Q(user__id__in=absent) | Q(user__id__in=leave))

    # Iterate through employees
    for employee in employees:
        employee_data = [
            employee.emp_id,
            employee.name,
            employee.company_contact if employee.company_contact else '',
            employee.personal_contact,
            employee.dob.strftime('%Y-%m-%d') if employee.dob else '',
            employee.doj.strftime('%Y-%m-%d') if employee.doj else '',
            employee.gender,
            employee.email if employee.email else '',
            employee.office_email,
            employee.designation,
            employee.level
        ]
        data.append(employee_data)

    # Create a table with styles
    style_table = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # ('PADDING', (0, 0), (-1, -1), 5),
    ]
    table = Table(data, style=style_table, repeatRows=1)

    # Create elements list and add the table
    elements = [table]

    # Build the PDF document with the elements list
    pdf.build(elements)

    # Get PDF content from BytesIO object
    pdf_bytes = buffer.getvalue()

    # Create a Django HttpResponse with PDF content as attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employee_report.pdf"'
    response.write(pdf_bytes)

    return response

def generate_employee_leave_report(request):

    if request.method == 'POST':
        id = request.POST['employee']
        employee = Employee.objects.filter(id=id).first()
    else:
         form = EmployeeLoginForm()

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    if not employee:
        return HttpResponse("Employee not found", status=404)
    
    user = employee.user  # Assuming 'user' is a ForeignKey field in the Employee model
    leaves = LeaveApplication.objects.filter(user=user)
    absents = Absent.objects.filter(user=employee)

    data = [
        ['date_from', 'date_to', 'reason']
    ]
    for leave in leaves:
        employee_data = [
            leave.date_from,
            leave.date_to,
            leave.reason
        ]
        data.append(employee_data)
    for absent in absents:
        employee_data = [
            absent.absent_on,
            absent.absent_on,
            "absent"
        ]
        data.append(employee_data)

    style_table = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 15),
    ])

    table = Table(data, style=style_table)
    elements = [table]

    pdf.build(elements)
    pdf_bytes = buffer.getvalue()

    # Create a Django HttpResponse with PDF content as attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="employee_report_{employee.id}.pdf"'
    response.write(pdf_bytes)

    return response





#$#$#$ EMPLOYEE #$#$#$
# Employee Login
def employeeLogin(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.groups.filter(name='EMPLOYEE'):
                    emp = Employee.objects.get(office_email=username)
                    if emp.employee_setup_completed == True:
                        auth_login(request,user)
                        return redirect('sidebar')
                    else:
                        return redirect('employeeSetupInitialization', username)
                else:
                    messages.success(request, 'Your account is not found')
            else:
                messages.success(request, 'Check your username and password')
    else:
         form = EmployeeLoginForm()

    context ={
        'form':form
    }
    return render(request,"employeeLogin.html", context)

# Employe Login Initial process
def employeeSetupInitialization(request, email):
    if request.method == 'POST':
        new_password = request.POST['newPassword']
        confirm_password = request.POST['confirmPassword']
        if new_password == confirm_password:
            employee = Employee.objects.get(office_email=email)
            print("yes")
            if request.user:
                try:                                                                                          
                    user = User.objects.get(username=email)
                    print("yes")
                    user.set_password(new_password)
                    user.save()
                    employee.employee_setup_completed = True
                    employee.save()
                    time.sleep(2)
                    return redirect('homepage')
                except Exception as e:
                    print(f"An exception occurred: {e}")
            else:
                messages.error(request, 'Invalid One Time Password')
        else:
            messages.error(request, 'Password and confirm password must be the same')
    return render(request, 'employeeLoginFirstTime.html')

# Employee Home Page
class CalendarViewEmp(generic.ListView):
    
    model = Event
    template_name = 'sidebar.html'
    
    @method_decorator(login_required(login_url='employeeLogin'))
    @method_decorator(user_passes_test(is_employee))
    def dispatch(self, *args, **kwargs):
        return super(CalendarViewEmp, self).dispatch(*args, **kwargs)   
    def dash(self):
        dict={}
        emp = Employee.objects.filter(office_email=self.request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
        leave = Leave.objects.filter(com_id=emp.com_id).all()[:3]
        for l in leave:
            cat_count = LeaveApplication.objects.filter(category__name=l, user=self.request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
            # dict[l]= cat_count
            if cat_count is None:
                cat_count = 0 
            dict[l]=[l.days-cat_count, l.days]  
        dic = {'com':com, 'dict':dict}       
        return dic      
    
    def quote(self):  
        emp = Employee.objects.filter(office_email=self.request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
        if self.request.method == 'GET': 
            quotedd = Quote.objects.filter(com_id = com).all().last()
            # quotedd = Quote.objects.get(tod_date = current_date, com_id = com)
            if quotedd is not None:
                quoted = quotedd.quotes
            else:
                quoted = "Waiting for Today's Quotes " 
        return  quoted
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emp = Employee.objects.filter(office_email=self.request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

        # use today's date for the calendar
        today = str(get_date(self.request.GET.get('day', None)))
        today_year, today_month, today_date = (int(x) for x in today.split('-'))
        
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        adminStatus = False
        cal = Calendar(d.year, d.month, today_date, today_month, today_year, adminStatus)
        html_cal = cal.formatmonth(com, withyear=True)
        context['calendar'] = mark_safe(html_cal)

        event = Eventcal(d.year, d.month, adminStatus)
        html_event = event.formatmonth(com, withyear=True)
        context['event'] = mark_safe(html_event)
        
        context['dic']=self.dash()
        context['quotes']=self.quote()
        context['emp'] = emp
        context['com'] = com
        return context

# Employee Profile
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def profileSetting(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    context = {'com':com}   
    return render(request,'profileSetting.html', context) 

# How To Use page for Employee
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def howToUse(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    context ={'com':com}  
    return render(request,"howToUse.html", context)  

# Leave Section
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveSection(request): 
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first() 
    context ={'com':com}      
    return render(request,'leaveSection.html', context)

# Leave Application
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveApplication(request):
    dic={}
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first() 
    event_list = list(Event.objects.filter(com_id=com, category='Public Holiday').values_list("date", flat=True))
    leave = Leave.objects.filter(com_id=emp.com_id).all()
    for l in leave:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic[l.name]= l.days-cat_count 
    dic = sorted(dic.items(), key=lambda x:x[1], reverse=True)  
    if request.method == 'POST':
        form = LeaveApplyForm(request.POST, com_id=com.id)
        status = request.POST.get('status')
        # print(status)
        print(form.errors)
        if form.is_valid():
            print(status)
            obj = form.save(commit = False)
            obj.user = request.user
            obj.status = status
            obj.save()
            return redirect('approvalStatus')
    else:
         form = LeaveApplyForm(com_id=com.id)

    context ={'form':form, 'dic':dic, 'com':com, 'event_list': event_list}
    return render(request,'leaveApplication.html', context)

@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def leaveApplicationAdmin(request, id):
    dic={}
    com = Company.objects.filter(username=request.user.username).first()
    emp_id = Employee.objects.get(pk = id)
    user_id = User.objects.get(username = emp_id.office_email)
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    event_list = list(Event.objects.filter(com_id=com, category='Public Holiday').values_list("date", flat=True))
    leave = Leave.objects.filter(com_id=com).all()
    for l in leave:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic[l.name]= l.days-cat_count 
    dic = sorted(dic.items(), key=lambda x:x[1], reverse=True)  
    if request.method == 'POST':
        form = LeaveApplyForm(request.POST, com_id=com.id)
        status = request.POST.get('status')
        # print(status)
        print(form.errors)
        if form.is_valid():
            print(status)
            obj = form.save(commit = False)
            obj.user = user_id
            obj.status = status
            obj.level1_approve = True
            obj.level1_comm = obj.level2_comm = obj.level0_comm = "Approved by HR"
            obj.level2_approve = True
            obj.status_approve = True
            obj.save()
            return redirect('activeEmployee')
    else:
         form = LeaveApplyForm(com_id=com.id)

    context ={'form':form, 'dic':dic, 'emp_id':id , 'com':com, 'event_list': event_list}
    return render(request,'leaveApplicationAdmin.html', context)

# Withdraw Leave Applications
@login_required(login_url='adminLogin')
@user_passes_test(is_employee)
def withdrawLeaveApplication(request, id):
    try:
        leave_application = LeaveApplication.objects.get(id=id)
        leave_application.delete()
        return redirect('approvalStatus')
    except LeaveApplication.DoesNotExist:
        print(f"Record with ID {id} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Leave Policy for Employee
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leavePolicy(request):  
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    leave = LeavePolicy.objects.filter(com_id=emp.com_id).all().first()
    count = Leave.objects.filter(com_id=emp.com_id).all().count()
    l1 = math.ceil(count/2)
    lea1 = Leave.objects.filter(com_id=emp.com_id).all()[:l1]
    lea2 = Leave.objects.filter(com_id=emp.com_id).all()[l1:]  
    context = {'leave':leave, 'lea1':lea1, 'lea2':lea2, 'com':com} 
    return render(request,'leavePolicy.html', context)

# Privacy Policy for Employee
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def privacyPolicy(request):  
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    privacy = PrivacyPolicy.objects.filter(com_id=com).first()  
    context = {'privacy':privacy, 'com':com} 
    return render(request,'privacyPolicy.html', context)

# Terms & Conditions for Employee
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def termsAndConditions(request):  
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    terms = Terms.objects.filter(com_id=com).first()  
    context = {'terms':terms, 'com':com} 
    return render(request,'termsAndConditions.html', context)

# Leave Application for Employee 
def leaveapplications(request):
    leave = Leave.objects.all()
    context = {'leave':leave}
    return render(request,'leaveapplications.html', context)

# Leave Basket
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveBasket(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    dic1 = {}
    dic2 = {}
    dic3 = {}
    leave = LeavePolicy.objects.filter(com_id=emp.com_id).all().first()
    count = Leave.objects.filter(com_id=emp.com_id).all().count()
    l1 = math.ceil(count/3)
    lea1 = Leave.objects.filter(com_id=emp.com_id).all()[:l1]
    for l in lea1:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic1[l]= [l.days-cat_count, l.days]
    lea2 = Leave.objects.filter(com_id=emp.com_id).all()[l1:l1*2]
    for l in lea2:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic2[l]= [l.days-cat_count, l.days]
    lea3 = Leave.objects.filter(com_id=emp.com_id).all()[l1*2:]
    for l in lea3:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic3[l]= [l.days-cat_count, l.days]
    context = {'leave':leave, 'dic1':dic1, 'dic2':dic2, 'dic3':dic3, 'com':com}
    return render(request, 'leaveBasket.html', context)


@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def leaveBasketAdmin(request, id):
    emp = Employee.objects.get(id=id)
    com = Company.objects.filter(name=emp.com_id).first()
    dic1 = {}
    dic2 = {}
    dic3 = {}
    leave = LeavePolicy.objects.filter(com_id=emp.com_id).all().first()
    count = Leave.objects.filter(com_id=emp.com_id).all().count()
    l1 = math.ceil(count/3)
    lea1 = Leave.objects.filter(com_id=emp.com_id).all()[:l1]
    for l in lea1:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=emp.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic1[l]= [l.days-cat_count, l.days]
    lea2 = Leave.objects.filter(com_id=emp.com_id).all()[l1:l1*2]
    for l in lea2:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=emp.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic2[l]= [l.days-cat_count, l.days]
    lea3 = Leave.objects.filter(com_id=emp.com_id).all()[l1*2:]
    for l in lea3:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=emp.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic3[l]= [l.days-cat_count, l.days]
    context = {'leave':leave, 'dic1':dic1, 'dic2':dic2, 'dic3':dic3, 'com':com, 'emp': emp}
    print(f'Dict1: {dic1}, Dict2: {dic2}, Dict3: {dic3}')
    return render(request, 'leaveBasketAdmin.html', context)


# Employee Approval Status
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def approvalStatus(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    today_date = timezone.now().date()
    leave = LeaveApplication.objects.filter(user=request.user)
    context ={'leave':leave, 'com':com, 'today':today_date}
    return render(request,'approvalStatus.html', context)

#$#$#$ EMPLOYEE Level 1 & 2 #$#$#$
# Leave Status Page for Level 1 & 2
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveStatus(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    if request.user.employee.level == 'Level 1':
        user = Employee.objects.get(user=request.user)
        leave= LeaveApplication.objects.filter(user__employee__department = user.department)
        context = {'leave':leave, 'com':com}
        return render(request,'leaveStatusL1.html', context)
    elif request.user.employee.level == 'Level 2':
        user = Employee.objects.get(user=request.user)
        leave = LeaveApplication.objects.filter(user__employee__reporting = user)
        context = {'leave':leave, 'com':com}
        return render(request,'leaveStatusL2.html', context)
    else:
        return redirect('sidebar')


# Leave Applications
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def leaveApplicationDetails(request):    
    com = Company.objects.filter(username=request.user.username).first()
    is_employee = False
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
        is_employee = True
    emps = Employee.objects.filter(com_id=com)
    emp_emails = emps.values_list('office_email', flat=True)
    leave= LeaveApplication.objects.filter(level1_approve=True, user__username__in=emp_emails)
    context = {'leave':leave,'com':com,'is_employee':is_employee}
    return render(request,'leaveApplicationDetails.html', context)


# Review Leave Status Page for Level 1 & 2
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def reviewLeaveApplication(request ,id):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    if request.user.employee.level == 'Level 1':
        leave = LeaveApplication.objects.get(id=id)
        form = LeaveLevel1Form(request.POST or None, instance=leave)
        if form.is_valid():
            form.save()
        context = {'leave':leave, 'form':form,'com':com}
        return render(request,'reviewLeaveApplicationL1.html', context)
    elif request.user.employee.level == 'Level 2':
        leave = LeaveApplication.objects.get(id=id)
        form = LeaveLevel2Form(request.POST or None, instance=leave)
        if form.is_valid():
            form.save()
        context = {'leave':leave, 'form':form,'com':com}
        return render(request,'reviewLeaveApplicationL2.html', context)
    else:    
        return redirect('sidebar')
    
# Approve Leave Page for Level 1 & 2
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)   
def approveLeave(request, id):
    if request.user.employee.level == 'Level 1':
        leave=get_object_or_404(LeaveApplication, pk=id)
        leave.level1_approve = True
        leave.level1_reject = False
        leave.save()
        return redirect('leaveStatus')
    elif request.user.employee.level == 'Level 2':
        leave=get_object_or_404(LeaveApplication, pk=id)
        leave.level2_approve = True
        leave.level2_reject = False
        leave.save()
        return redirect('leaveStatus')
    else:
        return redirect('sidebar')

# Reject Leave Page for Level 1 & 2
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)   
def rejectLeave(request, id):
    if request.user.employee.level == 'Level 1':
        leave=get_object_or_404(LeaveApplication, pk=id)
        if leave.level1_comm:
            leave.level1_approve = False
            leave.level1_reject = True
            leave.save()
            return redirect('leaveStatus')
        return redirect('reviewLeaveApplication', leave.id)
    elif request.user.employee.level == 'Level 2':
        leave=get_object_or_404(LeaveApplication, pk=id)
        if leave.level2_comm:
            leave.level2_approve = False
            leave.level2_reject = True
            leave.save()
            return redirect('leaveStatus')
        return redirect('reviewLeaveApplication', leave.id)
    else:
        return redirect('sidebar')

# Detail Leave Applications
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def reviewEmployeeApplication(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    leave= LeaveApplication.objects.get(id=id)
    context = {'leave':leave, 'com':com}
    return render(request,'reviewEmployeeApplication.html', context)

def reviewEmployeeApplicationEmployee(request, id):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    leave= LeaveApplication.objects.get(id=id)
    context = {'leave':leave, 'com':com}
    return render(request,'reviewLeaveApplicationL3.html', context)

# Approve Leave Page for Admin
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))  
def approveLeaveAdmin(request, id):
    leave=get_object_or_404(LeaveApplication, pk=id)
    leave.status_approve = True
    leave.status_reject = False
    leave.save()
    return redirect('leaveApplicationDetails')

# Reject Leave Page for Admin
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def rejectLeaveAdmin(request, id):
    leave=get_object_or_404(LeaveApplication, pk=id)
    leave.status_approve = False
    leave.status_reject = True
    leave.save()
    return redirect('leaveApplicationDetails')
#------------------------------------------------------------------------------------------------------
  
def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return date.today()


# Event add
def event(request, event_id=None):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()
        
    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        data = form.save(commit=False)
        data.com_id=com 
        data.save()
        return HttpResponseRedirect(reverse('adminDashboard'))
    return render(request, 'event.html', {'form': form})
 

def delete_event(request, event_id):
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()
    instance.delete()
    return redirect('adminDashboard')


def superadminlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            
            if user.groups.filter(name='SUPERADMIN').exists():
                login(request, user)
                return redirect('homeDashboard')  
            else:
                messages.error(request, "You don't have the required permissions.")
        else:
            messages.error(request, "There was an error in the login details.")
    
    return render(request, 'superadminlogin.html')



def logout_superuser(request):
    logout(request)
    # messages.success(request, "You have logout")
    return redirect('landingpage')

@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def feedback(request):
    com = Company.objects.filter(username=request.user.username).first()
    feedback = FeedbackModel.objects.filter(company_id=com.id)
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
        
    if request.method == 'POST':
        feedback_text = request.POST.get('name', '')
        company_id = request.POST.get('cid', '')
        company_instance = get_object_or_404(Company, id=company_id)
        feedback_instance = FeedbackModel.objects.create(text=feedback_text, company_id=company_instance)
        #return HttpResponse("Feedback submitted successfully!")
        return redirect('feedback')

    else:
        context = {'com': com, 'feedback': feedback}
        return render(request, 'feedback.html', context)
    
@login_required(login_url='employeeLogin')
# @user_passes_test(lambda u: is_admin(u) or is_hr(u))
def feedback_emp(request):

    
        
    if request.method == 'POST':
        feedback_text = request.POST.get('name', '')
        emp_id = request.POST.get('eid', '')
        to_dev = request.POST.get('to_dev', '')
        emp = Employee.objects.get(id=emp_id)
        print(to_dev)

        if to_dev == 'False':
            to_dev = False
        elif to_dev == 'True':
            to_dev = True
        
        print(to_dev)
        
        # company_instance = get_object_or_404(Company, id=company_id)
        FeedbackModel.objects.create(text=feedback_text, emp_id=emp, to_devs=to_dev)
        if to_dev == True:
            messages.success(request, "Feedback has been sent to the developers.")
        elif to_dev == False:
            messages.success(request, "Feedback has been sent to your company Admin.")


        return redirect('sidebar')

    return redirect('sidebar')
    
    
    
def companyfeedback(request):
    feedback_entries = FeedbackModel.objects.filter(company_id__isnull=False)
    context = {'feedback_entries': feedback_entries}
    return render(request, 'adminviewfeedback.html', context)

@login_required(login_url='adminLogin')
def feedbackEmp(request):
    com = Company.objects.filter(username=request.user.username).first()
    feedback = FeedbackModel.objects.filter(company_id=com.id)
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    feedback_entries = FeedbackModel.objects.filter(company_id__isnull=True, to_devs=False)
    context = {'feedback_entries': feedback_entries, 'com':com}
    return render(request, 'feedbackEmp.html', context)


def employeefeedback(request):
    feedback_entries = FeedbackModel.objects.filter(company_id__isnull=True, to_devs=True)
    context = {'feedback_entries': feedback_entries}
    return render(request, 'adminviewempfeedback.html', context)


def admincompanysupport(request):
    supports = Support.objects.all().order_by('-date')
    context = {'supports': supports}
    return render(request, 'adminviewsupport.html', context)


def viewfeedbackClient(request, feedback_id):
    
   
    feedback = get_object_or_404(FeedbackModel, pk=feedback_id)
    client = get_object_or_404(Company, pk=feedback.company_id.id)

    context = {
        'feedback': feedback,
        'client': client,
    }

    return render(request, 'viewfeedbackClient.html', context)

def viewemployeefeedbackClient(request, feedback_id):
    
   
    feedback = get_object_or_404(FeedbackModel, pk=feedback_id)
    client = get_object_or_404(Employee, pk=feedback.emp_id.id)

    context = {
        'feedback': feedback,
        'client': client,
    }

    return render(request, 'viewemployeefeedbackClient.html', context)

@login_required(login_url='adminLogin')
def viewemployeefeedbackCompany(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    feedback = FeedbackModel.objects.filter(company_id=com.id)
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
        
    feedback = FeedbackModel.objects.get(id=id)
    client = get_object_or_404(Employee, pk=feedback.emp_id.id)

    context = {
        'feedback': feedback,
        'client': client,
        'com': com,
    }
    return render(request, 'feedbackEmp.html', context)


def viewsupportClient(request, support_id):
    
    support = get_object_or_404(Support, pk=support_id)
    client = get_object_or_404(Company, pk=support.company_id.id)
   
    

    context = {
        'support': support,
        'client': client,
    }

    return render(request, 'viewsupportClient.html', context)


@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def supportcompany(request):
    if request.method == 'POST':
        namecontent = request.POST.get('namecontent', '')
        company_id = request.POST.get('cid', '')
        cname = request.POST.get('cname', '')
        cemailid = request.POST.get('cemailid', '')
        cwebsite = request.POST.get('cwebsite', '')
        cphone = request.POST.get('cphone', '')

        company = Company.objects.get(id=company_id)

        Support.objects.create(text = namecontent, company_id = company)

        # Send email
        subject = "Inquiry Support from Company"
        email_content = f"Name: {namecontent}\n\nCompany Name: {cname}\n\nEmail: {cemailid}\n\nWebsite: {cwebsite}\n\nPhone: {cphone}"
        send_mail(subject, email_content, 'noreply.leapss@gmail.com', ['noreply.leapss@gmail.com'], fail_silently=False)


        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Mail Sent ..'})
        else:
            # If it's not an AJAX request, return an HTML response
            context = {'success_message': 'Mail Sented ..'}
           
            return render(request, 'adminDashboard.html', context)


    else:
        return redirect('CalendarView')
    


# Backup of a company
def backup_list(request):
    backups = CompanyBackup.objects.filter(company=request.user)
    return render(request, 'backup_list.html', {'backups': backups})

# def create_backup(request):
#     com = Company.objects.filter(username=request.user.username).first()
#     if com is None:
#         emp = Employee.objects.filter(office_email=request.user.username).first()
#         com = Company.objects.filter(name=emp.com_id).first()

#     # Define the base directory for backups
#     base_directory = 'backups/'

#     # Check if the directory exists, if not, create it
#     if not os.path.exists(base_directory):
#         os.makedirs(base_directory)


#     # List of models to backup
#     models_to_backup = [
#         AllRequest, Company, Department, Employee, LeavePolicy, PrivacyPolicy, Terms, Leave, Quote, Event, LeaveApplication, Absent, FeedbackModel
#     ]

#     # Loop through each model to create a backup
#     for model in models_to_backup:
#         model_name = model.__name__
#         model_backup_path = os.path.join(base_directory, f'{model_name.lower()}_backup_{com.id}.json')
#         call_command('dumpdata', f'app.{model_name}', '--output', model_backup_path, '--pks', str(com.id))

#     # Save backup information to the database
#     backup_instance = CompanyBackup.objects.create(company=request.user, backup_file=os.path.join('backups_folder', f'combined_backup_{com.id}.zip'))

#     return redirect('backup_list')

def create_backup(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(office_email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()

    base_directory = 'backups/'

    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    models_to_backup = [
        Company, Department, Employee, LeavePolicy, PrivacyPolicy, Terms, Leave, Quote, Event, LeaveApplication, Absent,
        FeedbackModel
    ]

    # Define your encryption key or generate a new one securely
    key = b'WaO41lzHcg76QQ4siPdTcf0BUsuTnsTCMKJBSrmBack='
    cipher_suite = Fernet(key)

    encrypted_zip_buffer = BytesIO()

    with zipfile.ZipFile(encrypted_zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for model in models_to_backup:
            model_name = model.__name__
            model_backup_path = os.path.join(base_directory, f'{model_name.lower()}_backup_{com.id}.json')
            call_command('dumpdata', f'app.{model_name}', '--output', model_backup_path, '--pks', str(com.id))

            with open(model_backup_path, 'rb') as model_file:
                model_data = model_file.read()
                zip_file.writestr(f'{model_name.lower()}_backup_{com.id}.json', model_data)

            # Clean up the temporary JSON backup file
            os.remove(model_backup_path)

    encrypted_zip_buffer.seek(0)
    encrypted_data = cipher_suite.encrypt(encrypted_zip_buffer.read())

    response = HttpResponse(encrypted_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename=encrypted_combined_backup_{com.id}.zip'

    return response

def upload_backup(request):
    if request.method == 'POST':
        form = BackupUploadForm(request.POST, request.FILES)
        if form.is_valid():
            backup = form.save(commit=False)
            backup.company = request.user
            backup.save()
            return redirect('backup_list')
    else:
        form = BackupUploadForm()
    return render(request, 'upload_backup.html', {'form': form})

def retrieve_backup(request):
    if request.method == 'POST' and request.FILES.get('backup_file'):
        uploaded_file = request.FILES['backup_file']
        encrypted_data = uploaded_file.read()
        key = b'WaO41lzHcg76QQ4siPdTcf0BUsuTnsTCMKJBSrmBack='
        cipher_suite = Fernet(key)

        # Decrypt the backup data
        try:
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            decrypted_buffer = io.BytesIO(decrypted_data)
            with zipfile.ZipFile(decrypted_buffer, 'r') as zip_file:
                extracted_files = zip_file.namelist()  # List of files in the zip

                # Example: Read a specific file content
                # specific_file_content = zip_file.read('file_name_within_zip.txt')

            return render(request, 'retrieve_backup.html', {'extracted_files': extracted_files})
        except InvalidToken as e:
            print(f"Decryption failed: {e}")
    return render(request, 'retrieve_backup.html')

def queryresolve(request, id):

    if request.method == 'POST':
        query = Support.objects.get(id=id)
        query.resolved = True
        query.save()
        messages.success(request, f"Query with ticketID {query.id} has been resolved")
    
    return redirect('admincompanysupport')


def queryraise(request, id):

    query = Support.objects.get(id=id)
    if request.method == 'POST':
        query.resolved = False
        query.save()
        messages.success(request, f"Query with ticketID {query.id} has been raised again")
    
    return redirect('viewquery', id=query.id)

def querycomment(request, id):

    query = Support.objects.get(id=id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        query.comment = comment
        query.save()
        messages.success(request, f"Your comment has been added")
    
    return redirect('viewquery', id=query.id)


def viewquery(request, id):
    query = Support.objects.get(id=id)
    com = Company.objects.filter(username=request.user.username).first()

    return render(request, 'viewquery.html', {'query': query, 'com': com})

@login_required(login_url='adminLogin')
def employeereport(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    if emp is not None:
        com = Company.objects.filter(name=emp.com_id).first()
    else:
        com = Company.objects.filter(username=request.user.username).first()
    
    dep = Department.objects.filter(com_id_id=com.id)
   
    form = PerticularEmployeeForm(request.POST or None, request.FILES or None, com_id=com.id)
    employees = Employee.objects.filter(
                    com_id_id=com.id
                    
                )


    context = {'com': com, 'form': form, 'dep': dep, 'employees':employees}

    if request.method == 'POST':
        fromdate = request.POST.get('fromdate', '')
        todate = request.POST.get('todate', '')
        estatus = request.POST.get('estatus', '').lower()         
        department = request.POST.get('department', 'All')
        level = request.POST.get('level', 'All')
        fromemployee = request.POST.get('fromemployee', '')
        toemployee = request.POST.get('toemployee', '')
        

        try:
            
                queryset = Employee.objects.filter(
                    com_id_id=com.id                    
                )
                if fromdate !='' and todate !='':
                    fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                    todate = datetime.strptime(todate, '%Y-%m-%d').date()
                    queryset = queryset.filter(
                    doj__range=(fromdate, todate)
                    )
                if estatus != 'all':
                    if estatus == 'true':
                        estatus = True
                    elif estatus== 'false':
                        estatus=False
                    queryset = queryset.filter(status=estatus)
                if department != 'All':
                    queryset = queryset.filter(department_id=department)  
                if level != 'All':
                    queryset = queryset.filter(level=level) 
                if fromemployee !='All' and toemployee !='All':
                    regex_pattern = f'^[{fromemployee}-{toemployee}{fromemployee.upper()}-{toemployee.upper()}]'
                    #queryset = queryset.filter(name__iregex=r'^[a-dA-D]')
                    queryset = queryset.filter(name__iregex=regex_pattern)
                    

                context['employees'] = queryset
            
        except ValueError as e:
            print(f"Error parsing dates: {e}")

    return render(request, 'employeereport.html', context)

@login_required(login_url='adminLogin')
def leavereport(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    if emp is not None:
        com = Company.objects.filter(name=emp.com_id).first()
    else:
        com = Company.objects.filter(username=request.user.username).first()
    lea = Leave.objects.filter(com_id_id=com.id)
    
    dep = Department.objects.filter(com_id_id=com.id)
   
    form = PerticularEmployeeForm(request.POST or None, request.FILES or None, com_id=com.id)
    employees = Employee.objects.filter(
                    com_id_id=com.id
                    
                )
    leaves = LeaveApplication.objects.filter(
                    user_id__employee__com_id_id=com.id
                    
                ).select_related('user__employee','category')
      
    print(f"com_id: {com.id}")
    print(leaves)

    context = {'com': com, 'form': form, 'dep': dep, 'lea': lea, 'employees': employees, 'leaves': leaves}
    
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate', '')
        todate = request.POST.get('todate', '')
        leavetype = request.POST.get('leavetype', '')
        department = request.POST.get('department', '')
        employee = request.POST.get('employee', '')
        level = request.POST.get('level', '')
        fromemployee = request.POST.get('fromemployee', '')
        toemployee = request.POST.get('toemployee', '')
        try:
            if fromdate and todate:
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                todate = datetime.strptime(todate, '%Y-%m-%d').date()
                print(f"from_date: {fromdate}, to_date: {todate},  leavetype: {leavetype}, department: {department}, employee: {employee}, level: {level}, fromemployee: {fromemployee}, toemployee: {toemployee}")
                
                queryset = LeaveApplication.objects.filter(
                    user_id__employee__com_id_id=com.id,
                    apply_on__range=(fromdate, todate)
                ).select_related('user__employee','category')
                
                if department != 'All':
                    queryset = queryset.filter(user_id__employee__department=department)
                if level != 'All':
                    queryset = queryset.filter(user_id__employee__level=level)
                if employee != 'All':
                    queryset = queryset.filter(user_id__employee__id=employee)
                if fromemployee !='All' and toemployee !='All':
                    regex_pattern = f'^[{fromemployee}-{toemployee}{fromemployee.upper()}-{toemployee.upper()}]'
                    #queryset = queryset.filter(name__iregex=r'^[a-dA-D]')
                    queryset = queryset.filter(user_id__employee__name__iregex=regex_pattern)
                
                print(queryset)
                print('all condition is working')
                context['leaves'] = queryset
                
        except ValueError as e:
            print(f"Error parsing dates: {e}")
        
    return render(request, 'leavereport.html', context)
 


@login_required(login_url='adminLogin')
def attendancereport(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    if emp is not None:
        com = Company.objects.filter(name=emp.com_id).first()
    else:
        com = Company.objects.filter(username=request.user.username).first()
    lea = Leave.objects.filter(com_id_id=com.id)
    
    dep = Department.objects.filter(com_id_id=com.id)
   
    form = PerticularEmployeeForm(request.POST or None, request.FILES or None, com_id=com.id)

    employee_queryset = Employee.objects.filter(com_id_id=com.id)
    employees = Employee.objects.filter(com_id_id=com.id)
    
    data = []
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)
    dates = []
    event_list = list(Event.objects.filter(com_id=com, category='Public Holiday').values_list("date", flat=True))
    absent_list = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))

    while start_date <= end_date:
        dates.append(start_date)
        start_date += timedelta(days=1)

    for dt in dates:
        if dt.weekday() == 6 or (dt in event_list):          
            dates.remove(dt)

    
    for emp in employee_queryset:
                absent_list = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))

                for dt in dates:
                    dates_emp_present = []
                    dates_emp_present = dates
                    if dt in absent_list:
                        dates_emp_present.remove(dt)
                data.append([dates_emp_present, emp, 'Present'])
                dates_emp_absent = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))
                data.append([dates_emp_absent, emp, 'Absent'])

      
    print(f"com_id: {com.id}")

    context = {'com': com, 'form': form, 'dep': dep, 'lea': lea, 'employees': employees}
    
    if request.method == 'POST':
        department = request.POST.get('department', '')
        employee = request.POST.get('employee', '')
        level = request.POST.get('level', '')
        fromemployee = request.POST.get('fromemployee', '')
        toemployee = request.POST.get('toemployee', '')
        fromdate = request.POST.get('fromdate', '')
        todate = request.POST.get('todate', '')
        status = request.POST.get('status', '')

        
        if department != 'All':
            employee_queryset = employee_queryset.filter(department_id=department)
        if level != 'All':
            employee_queryset = employee_queryset.filter(level=level)
        if employee != 'All':
            employee_queryset = employee_queryset.filter(id=employee)
        if fromemployee !='All' and toemployee !='All':
            regex_pattern = f'^[{fromemployee}-{toemployee}{fromemployee.upper()}-{toemployee.upper()}]'
            #queryset = queryset.filter(name__iregex=r'^[a-dA-D]')
            employee_queryset = employee_queryset.filter(name__iregex=regex_pattern)
                
            print(employee_queryset)
            print('all condition is working')
            context['employee_queryset'] = employee_queryset

        if fromdate and todate:
            dates = []
            fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
            todate = datetime.strptime(todate, '%Y-%m-%d').date()
            print(f"from_date: {fromdate}, to_date: {todate}, department: {department}, employee: {employee}, level: {level}, fromemployee: {fromemployee}, toemployee: {toemployee}")
            delta = timedelta(days=1)

            while fromdate <= todate:
                dates.append(fromdate)
                fromdate += delta
            
            for dt in dates:
                if dt.weekday() == 6 or (dt in event_list):          
                    dates.remove(dt)

        if status == 'Present':
            data = []
            for emp in employee_queryset:
                absent_list = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))

                for dt in dates:
                    dates_emp = []
                    dates_emp = dates
                    if dt in absent_list:
                        dates_emp.remove(dt)
                data.append([dates_emp, emp, 'Present'])


        if status == 'Absent':
            data = []

            for emp in employee_queryset:
                dates_emp = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))

                data.append([dates_emp, emp, 'Absent'])
        
        if status == 'All':
            data = []
            for emp in employee_queryset:
                absent_list = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))

                for dt in dates:
                    dates_emp_present = []
                    dates_emp_present = dates
                    if dt in absent_list:
                        dates_emp_present.remove(dt)
                data.append([dates_emp_present, emp, 'Present'])
                dates_emp_absent = list(Absent.objects.filter(user=emp).values_list("absent_on", flat=True))
                data.append([dates_emp_absent, emp, 'Absent'])
      
    context['data'] = data
    context['employee_queryset'] = employee_queryset
    
    
    return render(request, 'attendancereport.html', context)
 
 
@login_required(login_url='adminLogin')
def eventreport(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    if emp is not None:
        com = Company.objects.filter(name=emp.com_id).first()
    else:
        com = Company.objects.filter(username=request.user.username).first()
    
    dep = Department.objects.filter(com_id_id=com.id)
   
    events = Event.objects.filter(com_id=com)

    print(f"com_id: {com.id}")

    categories = Event.objects.values_list('category', flat=True).distinct()

    context = {'com': com, 'dep': dep, 'events':events, 'categories': categories}

    if request.method == 'POST':
        fromdate = request.POST.get('fromdate', '')
        todate = request.POST.get('todate', '')
        category = request.POST.get('category', '')

        queryset = Event.objects.filter(com_id=com)

        if fromdate and todate:
            fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
            todate = datetime.strptime(todate, '%Y-%m-%d').date()
            queryset = queryset.filter(date__range=(fromdate, todate))

        if category != 'All':
            queryset = queryset.filter(category=category)

        context['events'] = queryset
            

    return render(request, 'eventreport.html', context)


@login_required(login_url='adminLogin')
def report(request):
    emp = Employee.objects.filter(office_email=request.user.username).first()
    if emp is not None:
        com = Company.objects.filter(name=emp.com_id).first()
    else:
        com = Company.objects.filter(username=request.user.username).first()
    
    dep = Department.objects.filter(com_id_id=com.id)
   
    events = Event.objects.filter(com_id=com)

    print(f"com_id: {com.id}")

    categories = Event.objects.values_list('category', flat=True).distinct()

    context = {'com': com, 'dep': dep, 'events':events, 'categories': categories}
    

    return render(request, 'report.html', context)

