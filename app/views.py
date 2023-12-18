from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from datetime import datetime, date, timedelta
import calendar, math
import string, random
from django.urls import reverse
from .utils import Calendar, Eventcal 
from django.utils.safestring import mark_safe 
from django.views import generic
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q, Count, Sum
from .helper import send_account_creation_mail, send_company_login_credential_mail, send_admin_forgot_password_otp

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
    return render(request,"landingpage.html")

# Home Page
def homepage(request):
    return render(request,"homePage.html")

# Request LEAPSS app
def requestApplication(request):
    print('hii')
    if request.method == 'POST':
        print('hello')
        form = AppRequestForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)            
            instance.active_status = True
            instance.username = instance.email
            instance.save()
            return render(request, 'successfullyApply.html')
        else:
            print(form.errors)
            messages.success(request, 'Check your data')
    else:
        form = AppRequestForm()

    context ={
        'form':form
    }
    return render(request, 'applyApplication.html', context)

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

def approvedClientDashboard(request):
    clients = AllRequest.objects.filter(approve_status=True).all()
    context ={
        'clients':clients
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
    print(custom_password)
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
                    return redirect('newCompanySetup', username=username)
            else:
                return redirect('appDisabled')
        except Company.DoesNotExist:
            messages.error(request, 'Invalid credentials')
        except AllRequest.DoesNotExist:
            messages.error(request, 'Company Not Found')
    return render(request, 'companyLogin.html')

def newCompanySetup(request, username):
    if request.method == 'POST':
        old_password = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        confirm_password = request.POST['confirmPassword']
        if new_password == confirm_password:
            try:
                company = Company.objects.get(username=username, password=old_password)
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
                    response = redirect('homepage')
                    response.set_cookie('company_id', company.id)
                    return response
                else:
                    messages.warning(request, 'Superuser already exists')
            except Company.DoesNotExist:
                messages.error(request, 'Company not found or incorrect password')
        else:
            messages.error(request, 'Password and confirm password must be the same')

    return render(request, 'newCompanySetup.html')

def adminForgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            valid_email = Company.objects.get(email=email).email
            otp = str(random.randint(100000, 999999))
            send_admin_forgot_password_otp(otp, email)
            return redirect('changeAdminPassword', otp=otp , email=valid_email)
        except Company.DoesNotExist:
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
                    print(email)
                    company = Company.objects.get(email=email)
                    superuser = User.objects.get(username=email)
                    company.password = new_password
                    company.save()
                    superuser.set_password(new_password)
                    superuser.save()
                    return redirect('adminLogin')
                # except Company.DoesNotExist:
                #     messages.error(request, 'Company not found or incorrect password')
                except Exception as e:
                    # Handle the exception
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
        if com is None:
            emp = Employee.objects.filter(email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
        emails = Employee.objects.filter(com_id=com).values_list('email', flat=True)
        today = datetime.today().strftime("%Y-%m-%d")
        total_emp = Employee.objects.filter(status=True, com_id = com).count()
        onleave = LeaveApplication.objects.filter(user__employee__status=True,status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails).count()
        absent_count = Absent.objects.filter(absent_on = today).count()
        present_today = total_emp - (onleave + absent_count)
        total_leave = onleave + absent_count
        apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True, user__username__in=emails).count()

        dic ={'com':com.name, 'total_emp':total_emp, 'present_today':present_today, 'onleave':onleave, 'total_leave':total_leave, 'apply_leav':apply_leav}       
        return dic 
    
    def quotesub(self): 
        com = Company.objects.filter(username=self.request.user.username).first()
        if com is None:
            emp = Employee.objects.filter(email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
        quote = Quote.objects.all().last() 
        form = QuoteForm()
        if quote is None:
            if self.request.method == "GET": 
                form = QuoteForm(self.request.GET)
                if form.is_valid():
                    data = form.save(commit=False)
                    data.com_id=com
                    data.save()
                    return redirect('adminDashboard')   
            else:
                form = QuoteForm()
        else:
            instance = Quote.objects.filter(com_id = com).last()
            form = QuoteUpdateForm(self.request.GET or None, instance=instance)
            if form.is_valid():
                form.save()
        quotes = {'quote':quote,'form':form}
        return quotes

    def quote(self):    
        com = Company.objects.filter(username=self.request.user.username).first()
        if com is None:
            emp = Employee.objects.filter(email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
        if self.request.method == "GET":  
            current_date = 0 
            current_date = datetime.now().strftime('%Y-%m-%d')  
            try:
                quotedd = Quote.objects.get(tod_date = current_date, com_id = com)
                quoted = quotedd.quotes
            except Quote.DoesNotExist:
                quoted = None

            if quoted:   
                return quoted   
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        com = Company.objects.filter(username=self.request.user.username).first()
        if com is None:
            emp = Employee.objects.filter(email=self.request.user.username).first()
            com = Company.objects.filter(name=emp.com_id).first()
        # use today's date for the calendar
        adminStatus = True
        today = str(get_date(self.request.GET.get('day', None)))
        today_year, today_month, today_date = (int(x) for x in today.split('-'))
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
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
        return context

# Total Employee
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def totalEmployees(request): 
    com = Company.objects.filter(username=request.user.username).first()
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
@user_passes_test(is_admin)
def totalEmployeeDetails(request, id):
    com = Company.objects.filter(username=request.user.username).first()
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
@user_passes_test(is_admin)
def presentEmployees(request):
    com = Company.objects.filter(username=request.user.username).first()
    emails = Employee.objects.filter(com_id=com).values_list('email', flat=True)
    today = datetime.today().strftime("%Y-%m-%d")
    total_emp = Employee.objects.filter(status=True, com_id = com).count()
    onleave = LeaveApplication.objects.filter(user__employee__status=True, status_approve=True, date_from__lte=today, date_to__gte=today, user__username__in=emails).count()
    absent_count = Absent.objects.filter(absent_on = today, user__user__username__in=emails).count()
    present_today = total_emp - (onleave + absent_count)
    total_leave = onleave + absent_count 
    apply_leav = LeaveApplication.objects.filter(status_approve=False, status_reject=False, level1_approve=True).count()
    
    leave = LeaveApplication.objects.filter(status_approve=True, date_from__lte=today, date_to__gte=today).values('user__id')
    absent = Absent.objects.filter(absent_on=today, user__user__username__in=emails).values('user__user__id')
    present = Employee.objects.filter(user__username__in=emails).exclude(Q(user__id__in = absent) | Q(user__id__in = leave))
    print(present)
    context = {'total_emp':total_emp, 'present_today':present_today, 'onleave':onleave, 'total_leave':total_leave, 'apply_leav':apply_leav, 'present':present, 'com':com}
    return render(request,'presentEmployees.html', context)


# On leave page
@login_required(login_url='adminLogin')
@user_passes_test(is_admin)
def onLeave(request):
    com = Company.objects.filter(username=request.user.username).first()
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
    context = {'total_emp':total_emp, 'present_today':present_today, 'onleave':onleave, 'leav':leav, 'form':form, 'absent':absent, 'absent_count':absent_count, 'total_leave':total_leave,'apply_leav':apply_leav}
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
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter(status=True, com_id=com).order_by('name')
    context = {'emp':emp,'com':com}
    return render(request, 'activeEmployee.html', context)

# Deactivate detail employee page 
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def deactivateDetail(request, id):
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
    context = {'form':form}
    return render(request, 'deactivate.html', context)

# Inactive Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def inactiveEmployee(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter(status=False, com_id=com)
    context = {'emp':emp,'com':com}
    return render(request, 'inactiveEmployee.html', context)

# Deactivate detail employee page 
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def activateDetail(request, id):
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
    context = {'form':form}
    return render(request, 'activate.html', context)

# Add Employee Detail
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def addEmployee(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.filter(level = 'Level 1' or 'Level 2')
    if request.method == "POST":
        form = AddEmployeeExtraForm(request.POST)
        form1 = AddEmployeeForm(request.POST, request.FILES, com_id=com.id)
        if form.is_valid() and form1.is_valid():
            name = request.POST['name']
            office_email = request.POST['office_email']
            username = request.POST['username']
            password = request.POST['password']
            company = com.name
            user=form.save()
            user.set_password(user.password)
            user.save()
            f2=form1.save(commit=False)
            f2.user=user
            f2.com_id=com
            user1=f2.save()
            
            send_account_creation_mail(office_email, name, company, username, password)
            print(f2.level)
            group=Group.objects.get_or_create(name='EMPLOYEE')
            group[0].user_set.add(user)
            if f2.level == "Level 0":
                group=Group.objects.get_or_create(name='HR')
                group[0].user_set.add(user)
            return redirect('activeEmployee')
    else:
        form = AddEmployeeExtraForm()
        form1 = AddEmployeeForm(com_id=com.id)
    context={'form':form, 'form1':form1, 'emp':emp,'com':com}
    return render(request, 'addEmployee.html', context)

# View Employee Details
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def viewEmployee(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emp = Employee.objects.get(id=id)
    context = {'emp':emp,'com':com}
    return render(request,'employeeProfile1.html', context) 

# Edit Employee Details
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def editEmployee(request,id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    data = Employee.objects.get(id=id)
    instance = Employee.objects.get(pk=id)
    instance1=User.objects.get(pk=instance.user.id)
    form = EmployeeUpdateForm(request.POST or None, request.FILES or None, instance=instance)
    form1 = EmployeeUpdateExtraForm(request.POST or None, instance=instance1)
    if form.is_valid() and form1.is_valid():
        form.save()
        form1.save()
        return redirect('activeEmployee')

    context = {'form':form, 'form1':form1, 'data':data,'com':com}
    return render(request,'editEmployee.html', context) 

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
        emp = Employee.objects.filter(email=request.user.username).first()
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
def editCompany(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    instance = Company.objects.get(pk=id)
    form = CompanyUpdateForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('companySetup')
    else:
        print(form.errors)
    context = {'form':form, 'com':com}
    return render(request, 'editCompany.html', context)

# Department
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def department(request):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
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
        emp = Employee.objects.filter(email=request.user.username).first()
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
        emp = Employee.objects.filter(email=request.user.username).first()
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
@user_passes_test(is_admin) 
def deleteDepartment(request, id):
    list =[]
    dep = Department.objects.get(id=id)
    dep_count = Employee.objects.values('department__department','department').filter(status=True).annotate(emp_count=Count('emp_id'))
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
        emp = Employee.objects.filter(email=request.user.username).first()
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
                return redirect('leavePolicySetting')
            else:
                print(form.errors)
        else:
            form = LeavePolicyForm(initial={'com_id': com.id})
    else:
        instance = LeavePolicy.objects.get(pk=leave.id)
        form = LeavePolicyUpdateForm(request.POST or None, instance=instance, initial={'com_id': com.id})
        if request.method == "POST":
            if form.is_valid():
                form.save()
                return redirect('leavePolicySetting')
            else:
                print(form.errors)

    context = {'leave': leave, 'form': form, 'lea1': lea1, 'lea2': lea2, 'com': com}
    return render(request, "leavePolicySetting.html", context)


# Add Leave
def addLeave(request):
    form = AddLeaveForm()
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
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
    com = Company.objects.all().first()
    instance = Leave.objects.get(id=id)
    form = EditLeaveForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('leavePolicySetting')

    context = {'form':form, 'com':com}
    return render(request,'editLeave.html', context)

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
                    auth_login(request,user)
                    return redirect('sidebar')
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
        emp = Employee.objects.filter(email=self.request.user.username).first()
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
        emp = Employee.objects.filter(email=self.request.user.username).first()
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
        emp = Employee.objects.filter(email=self.request.user.username).first()
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
        return context

# Employee Profile
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def profileSetting(request):
    emp = Employee.objects.filter(email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    context = {'com':com}   
    return render(request,'profileSetting.html', context) 

# How To Use page for Employee
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def howToUse(request):
    emp = Employee.objects.filter(email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    context ={'com':com}  
    return render(request,"howToUse.html", context)  

# Leave Section
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveSection(request): 
    emp = Employee.objects.filter(email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first() 
    context ={'com':com}      
    return render(request,'leaveSection.html', context)

# Leave Application
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveApplication(request):
    dic={}
    emp = Employee.objects.filter(email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first() 
    leave = Leave.objects.filter(com_id=emp.com_id).all()
    for l in leave:
        cat_count = LeaveApplication.objects.filter(category__name=l, user=request.user, status_approve = True).aggregate(Sum('leave_count'))['leave_count__sum']
        if cat_count is None:
            cat_count = 0
        dic[l.name]= l.days-cat_count 
    dic = sorted(dic.items(), key=lambda x:x[1], reverse=True)  
    if request.method == 'POST':
        form = LeaveApplyForm(request.POST, com_id=com.id)
        if form.is_valid():
            obj = form.save(commit = False)
            obj.user = request.user
            obj.save()
            return redirect('approvalStatus')
    else:
         form = LeaveApplyForm(com_id=com.id)

    context ={'form':form, 'dic':dic, 'com':com}
    return render(request,'leaveApplication.html', context)

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
    emp = Employee.objects.filter(email=request.user.username).first()
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
    emp = Employee.objects.filter(email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    privacy = PrivacyPolicy.objects.filter(com_id=com).first()  
    context = {'privacy':privacy, 'com':com} 
    return render(request,'privacyPolicy.html', context)

# Terms & Conditions for Employee
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def termsAndConditions(request):  
    emp = Employee.objects.filter(email=request.user.username).first()
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
    emp = Employee.objects.filter(email=request.user.username).first()
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
    print(dic3,dic2,dic1,"dic")
    return render(request, 'leaveBasket.html', context)
# Employee Approval Status
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def approvalStatus(request):
    emp = Employee.objects.filter(email=request.user.username).first()
    com = Company.objects.filter(name=emp.com_id).first()
    leave = LeaveApplication.objects.filter(user=request.user)
    context ={'leave':leave, 'com':com}
    return render(request,'approvalStatus.html', context)

#$#$#$ EMPLOYEE Level 1 & 2 #$#$#$
# Leave Status Page for Level 1 & 2
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def leaveStatus(request):
    emp = Employee.objects.filter(email=request.user.username).first()
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
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    emps = Employee.objects.filter(com_id=com)
    emp_emails = emps.values_list('email', flat=True)
    leave= LeaveApplication.objects.filter(level1_approve=True, user__username__in=emp_emails)
    context = {'leave':leave,'com':com}
    return render(request,'leaveApplicationDetails.html', context)


# Review Leave Status Page for Level 1 & 2
@login_required(login_url='employeeLogin')
@user_passes_test(is_employee)
def reviewLeaveApplication(request ,id):
    emp = Employee.objects.filter(email=request.user.username).first()
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
        else:
            print('None')
        return redirect('reviewLeaveApplication', leave.id)
    elif request.user.employee.level == 'Level 2':
        leave=get_object_or_404(LeaveApplication, pk=id)
        if leave.level2_comm:
            leave.level2_approve = False
            leave.level2_reject = True
            leave.save()
            return redirect('leaveStatus')
        else:
            print('None')
        return redirect('reviewLeaveApplication', leave.id)
    else:
        return redirect('sidebar')

# Detail Leave Applications
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def reviewEmployeeApplication(request, id):
    com = Company.objects.filter(username=request.user.username).first()
    if com is None:
        emp = Employee.objects.filter(email=request.user.username).first()
        com = Company.objects.filter(name=emp.com_id).first()
    leave= LeaveApplication.objects.get(id=id)
    context = {'leave':leave, 'com':com}
    return render(request,'reviewEmployeeApplication.html', context)

def reviewEmployeeApplicationEmployee(request, id):
    emp = Employee.objects.filter(email=request.user.username).first()
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
        emp = Employee.objects.filter(email=request.user.username).first()
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