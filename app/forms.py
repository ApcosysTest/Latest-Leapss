from django import forms  
from .models import *
from django.forms import ModelForm, DateInput, ModelChoiceField
from datetime import datetime, date
from django.db.models.functions import Concat
from django.db.models import Value 


# Admin Login Form
class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}), required=True)

class AppRequestForm(forms.ModelForm):  
    company_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Company Name'}))
    website = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Company Website'}), required=False)
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Email ID'}))
    telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Phone Number'}))
    telephone1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Alternate Number'}), required=False)
    country = forms.CharField(widget=forms.TextInput())
    state = forms.CharField(widget=forms.TextInput())
    city = forms.CharField(widget=forms.TextInput())
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Address'}))
    pincode = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Pincode'}))
    # username = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = AllRequest 
        fields = ['company_name', 'website', 'email', 'telephone', 'telephone1', 'city', 'state', 'country', 'address', 'pincode']

class CompanySetupForm(forms.ModelForm):  
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Company Name'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Email ID'}))
    website = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Website'}))
    telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Phone Number'}))
    telephone1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Phone Number'}), required=False)
    telephone2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Phone Number'}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Address'}))
    pincode = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Pincode'}))
    country = forms.CharField(widget=forms.TextInput())
    state = forms.CharField(widget=forms.TextInput())
    city = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Company 
        fields = "__all__"

# Company update Form
class CompanyUpdateForm(forms.ModelForm):  
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Company Name'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Email ID'}))
    website = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Website'}))
    telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Telephone'}))
    telephone1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Telephone 1'}), required=False)
    telephone2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Telephone 2'}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Address'}))
    pincode = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Pincode'}))
    country = forms.CharField(widget=forms.TextInput())
    state = forms.CharField(widget=forms.TextInput())
    city = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Company 
        fields = ['name', 'email', 'website', 'telephone', 'telephone1', 'telephone2', 'address', 'pincode', 'city', 'state', 'country']

# Company Department Form
class CompanyDepForm(forms.ModelForm):
    department = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Department'}))
    dep_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Department Code'}))

    class Meta:
        model = Department
        fields = "__all__"
        widgets = {
            'com_id': forms.HiddenInput(),
        }

# Company Department Update Form
class CompanyDepUpdateForm(forms.ModelForm):
    department = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Department'}))
    dep_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Department Code'}))

    class Meta:
        model = Department
        fields = "__all__"
        widgets = {
            'com_id': forms.HiddenInput(),
        }

class NameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name} ({obj.emp_id})'
    
LEVELS = (
    ("","Select Level"),
    ("Level 0", "HR"),
    ("Level 1", "Senior Official"),
    ("Level 2", "Team Lead"),
    ("Level 3", "Employee")
)
GENDER = (
    ("","Select Gender"),
    ("Male","Male"),
    ("Female","Female"), 
    ("Other","Other")
)

# Add Employee Form
class AddEmployeeForm(forms.ModelForm):
    emp_id = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Employee Id', 'id': 'emp_id', 'name': 'emp_id'}), label='Employee ID')
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Employee Name'}), label='Employee Name')
    company_contact = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Official Number'}),required=False, label='Official Number')
    personal_contact = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Personal Number'}), label='Personal Number')
    present_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Present Address'}),required=False, label='Present Address')
    permanent_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Permanent Address'}),required=False, label='Permanent Address')
    dob = forms.DateField(widget=forms.DateInput(format=('%d-%m-%Y'),attrs={'class': 'datepicker', 'placeholder': 'Select a date', 'type': 'date'}), label='Date Of Birth')
    doj = forms.DateField(widget=forms.DateInput(format=('%d-%m-%Y'),attrs={'class': 'datepicker', 'placeholder': 'Select a date', 'type': 'date'}), label='Date of Joining')
    gender = forms.ChoiceField(choices=GENDER,widget=forms.Select(), label='Gender')
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Personal Email ID', 'id': 'email', 'name': 'email'}),required=False, label='email')
    office_email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Official Email ID', 'id': 'official_email', 'name': 'official_email'}),required=False, label='Official Email')
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class':'form-control'}), required=False, label='Image')
    designation = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Designation'}), label='Designnation')
    level = forms.ChoiceField(choices=LEVELS, widget=forms.Select(), label='Level')
    department = forms.ModelChoiceField(queryset=Department.objects.all(),widget=forms.Select(), empty_label="Select Department", required=True, label='Department')
    reporting = NameChoiceField(queryset=Employee.objects.order_by('name').filter(Q(level='Level 0') | Q(level='Level 1') | Q(level='Level 2')).exclude(status=False),widget=forms.Select(attrs={ }), empty_label="Select Reporting Person", required=False, label='Reporting Person')

    def __init__(self, *args, **kwargs):
        com = kwargs.pop('com_id', None)
        super(AddEmployeeForm, self).__init__(*args, **kwargs)
        
        if com:
            self.fields['department'] = forms.ModelChoiceField(queryset=Department.objects.filter(com_id = com).all(),widget=forms.Select(), empty_label="Select Department", required=True)
            self.fields['reporting'] = NameChoiceField(queryset=Employee.objects.order_by('name').filter(Q(level='Level 0') | Q(level='Level 1') | Q(level='Level 2'), com_id = com).exclude(status=False),widget=forms.Select(attrs={ }), empty_label="Select Reporting Person", required=False)

    class Meta:  
        model = Employee
        fields = ['emp_id', 'name','gender','office_email', 'personal_contact','company_contact', 'present_address','permanent_address', 'dob', 'doj','email', 'image', 'designation','level', 'department', 'reporting']
        widgets = {
            'com_id': forms.HiddenInput(),
        }

class AddEmployeeExtraForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Must be Company\'s E-mail Id', 'id': 'username', 'name': 'username'}), required=True, label='Username')
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Minimum 8 and 1 special character','id':'Password'}), required=True)
    # confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password','id':'Confirm_Password','onkeyup':'validate_password()'}), required=True)

    class Meta:
        model=User
        fields=['username']

    # def clean(self):
    #     special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
    #     cleaned_data=super(AddEmployeeExtraForm, self).clean()
    #     password=cleaned_data.get("password")
    #     confirm_password=cleaned_data.get("confirm_password")
    #     username =cleaned_data.get('username')

    #     if len(username) < 8:
    #         self.add_error('username','Username length must be greater than 8 character.')
    #     if not any (char in special_characters for char in password):
    #         self.add_error('password','Password must contain at least one special Character.')

    #     if len(password)  < 8:
    #         self.add_error('password','Password length must be greater than 8 character.')
    #     if not any (char.isdigit() for char in password):
    #         self.add_error('password','Password must contain at least one digit.')
    #     if not any (char in special_characters for char in password):
    #         self.add_error('password','Password must contain at least one special Character.')

    #     if password != confirm_password:
    #         self.add_error('confirm_password', "Password does not Match")

    #     return cleaned_data
    
# Employee Update Form
class EmployeeUpdateForm(forms.ModelForm):
    emp_id = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Employee Id'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Employee Name'}))
    company_contact = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Official Number'}),required=False)
    personal_contact = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Personal Number'}))
    present_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Present Address'}),required=False)
    permanent_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Permanent Address'}),required=False)
    dob = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'date'}))
    doj = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER,widget=forms.Select())
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Personal Email ID'}),required=False)
    office_email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Official Email ID'}),required=False)
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class':'form-control','id':'fileUp'}), required=False) 
    designation = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Designation'}))
    level = forms.ChoiceField(choices=LEVELS,widget=forms.Select())
    department = forms.ModelChoiceField(queryset=Department.objects.all(),widget=forms.Select(), empty_label="Select Department", required=True)
    reporting = NameChoiceField(queryset=Employee.objects.order_by('name').filter(Q(level='Level 0') | Q(level='Level 1') | Q(level='Level 2')).exclude(status=False),widget=forms.Select(), empty_label="Select Reporting Person", required=False)

    def __init__(self, *args, **kwargs):
        com = kwargs.pop('com_id', None)
        super(EmployeeUpdateForm, self).__init__(*args, **kwargs)
        
        if com:
            self.fields['department'] = forms.ModelChoiceField(queryset=Department.objects.filter(com_id = com).all(),widget=forms.Select(), empty_label="Select Department", required=True)
            self.fields['reporting'] = NameChoiceField(queryset=Employee.objects.order_by('name').filter(Q(level='Level 0') | Q(level='Level 1') | Q(level='Level 2'), com_id = com).exclude(status=False),widget=forms.Select(attrs={ }), empty_label="Select Reporting Person", required=False)

    
    class Meta:  
        model = Employee
        fields = ['emp_id', 'name','gender','office_email', 'personal_contact','company_contact', 'present_address','permanent_address', 'dob', 'doj','email', 'image', 'designation','level', 'department', 'reporting']

class PerticularEmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        com = kwargs.pop('com_id', None)
        super(PerticularEmployeeForm, self).__init__(*args, **kwargs)
        
        if com:
            self.fields['employee'] = NameChoiceField(queryset=Employee.objects.order_by('name').filter(com_id = com).exclude(status=False),widget=forms.Select(attrs={ }), empty_label="Select Employee", required=True)
        
    class Meta:
        model=Employee
        fields=['name']


class EmployeeUpdateExtraForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Must be Company\'s E-mail Id'}), required=True)
    
    class Meta:
        model=User
        fields=['username']
        
class DeactivateForm(forms.ModelForm):
    deactivate = forms.CharField(widget=forms.Textarea(attrs=({'id':'quoted','placeholder':'Reason',})))
    
    class Meta:
        model = Employee
        fields= ['deactivate']
        
class ActivateForm(forms.ModelForm):
    activate = forms.CharField(widget=forms.Textarea(attrs=({'id':'quoted','placeholder':'Reason',})))
    
    class Meta:
        model = Employee
        fields= ['activate']

# Quote form
class QuoteForm(forms.ModelForm):
    quotes = forms.CharField(widget=forms.Textarea(attrs=({'id':'quote','placeholder':'Information of the day','oninput':'auto_grow(this)'})))
     
    class Meta:  
        model = Quote
        fields = ['quotes'] 
        widgets = {
            'com_id': forms.HiddenInput(),
        }
   
# Quote Update form
class QuoteUpdateForm(forms.ModelForm):
    quotes = forms.CharField(widget=forms.Textarea(attrs=({'id':'quote','placeholder':'Informtion of the day','oninput':'auto_grow(this)'})))
     
    class Meta:  
        model = Quote
        fields = ['quotes']
   
choice = [('True','Admin Only   '),('False', 'Both')]
class EventForm(ModelForm):
    class Meta:
        model = Event
        # datetime-local is a HTML5 input type, format to make date time show on fields
        widgets = {
            'date': DateInput(format='%Y-%m-%d',attrs={'class': 'datepicker', 'type': 'date'}),
            'visibility' : forms.RadioSelect(choices=choice),
            'com_id': forms.HiddenInput()
        }
        fields = '__all__'     

# Leave Policy Form
class LeavePolicyForm(forms.ModelForm):
    leavepolicy = forms.CharField(widget=forms.Textarea())

    class Meta:  
        model = LeavePolicy
        fields = ['leavepolicy'] 
        widgets = {
            'com_id': forms.HiddenInput(),
        }

# Privacy Policy Form
class PrivacyPolicyForm(forms.ModelForm):
    privacypolicy = forms.CharField(widget=forms.Textarea())

    class Meta:  
        model = PrivacyPolicy
        fields = ['privacypolicy'] 
        widgets = {
            'com_id': forms.HiddenInput(),
        }

# T&C Form
class TermsForm(forms.ModelForm):
    terms = forms.CharField(widget=forms.Textarea())

    class Meta:  
        model = Terms
        fields = ['terms'] 
        widgets = {
            'com_id': forms.HiddenInput(),
        }

# Leave Policy Update Form
class LeavePolicyUpdateForm(forms.ModelForm):
    leavepolicy = forms.CharField(widget=forms.Textarea(attrs=({'id':'tarea', 'placeholder': 'Fill in your leave policy'})))
    class Meta:  
        model = LeavePolicy
        fields = '__all__'

# Privacy Policy Update Form
class PrivacyPolicyUpdateForm(forms.ModelForm):
    privacypolicy = forms.CharField(widget=forms.Textarea(attrs=({'id':'tarea', 'placeholder': 'Fill in your privacy policy'})))
    class Meta:  
        model = PrivacyPolicy
        fields = ['privacypolicy']

# T&C Update Form
class TermsUpdateForm(forms.ModelForm):
    terms = forms.CharField(widget=forms.Textarea(attrs=({'id':'tarea', 'placeholder': 'Fill in your Terms And Conditions'})))
    class Meta:  
        model = Terms
        fields = ['terms']
 
# Add Leave Form
class AddLeaveForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    days = forms.IntegerField()

    class Meta:
        model = Leave
        fields = '__all__'
        widgets = {
            'com_id': forms.HiddenInput(),
        }

# Edit Leave Form
class EditLeaveForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    days = forms.IntegerField()

    class Meta:
        model = Leave
        fields = '__all__'
        widgets = {
            'com_id': forms.HiddenInput(),
        }

# Employee Login Form
class EmployeeLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}), required=True)

# Employee Leave Apply Form
class LeaveApplyForm(forms.ModelForm):
    # category = forms.ModelChoiceField(queryset=Leave.objects.filter(~Q(days = 0)),widget=forms.Select(), empty_label="---Select Leave Category---", required=True)
    date_from = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker-from', 'id':'datepicker-from', 'type': 'date','onclick':"enableTo()"}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker-to', 'id':'datepicker-to', 'type': 'date','disabled':'True','onclick':"minDate()"}))
    reason = forms.CharField(widget=forms.Textarea(attrs={'placeholder':"Reason"}))
    leave_count = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        com = kwargs.pop('com_id', None)
        super(LeaveApplyForm, self).__init__(*args, **kwargs)
        
        if com:
            self.fields['category'] = forms.ModelChoiceField(queryset=Leave.objects.filter(~Q(days = 0), com_id = com),widget=forms.Select(), empty_label="---Select Leave Category---", required=True)

    class Meta:
        model = LeaveApplication
        fields = ['category', 'date_from', 'date_to', 'reason', 'leave_count']

# Leave Comment from Level 2
class LeaveLevel2Form(forms.ModelForm):
    level2_comm = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=True)

    class Meta:
        model = LeaveApplication
        fields = ['level2_comm']

# Leave Comment from Level 1
class LeaveLevel1Form(forms.ModelForm):
    level1_comm = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=True)

    class Meta:
        model = LeaveApplication
        fields = ['level1_comm']        

# Leave Comment from Level 0
class LeaveLevel0Form(forms.ModelForm):
    level0_comm = forms.CharField(widget=forms.Textarea(attrs={'rows':'3'}), required=True)

    class Meta:
        model = LeaveApplication
        fields = ['level0_comm']  

# Absent Form
today = datetime.today().strftime("%Y-%m-%d")
leave = LeaveApplication.objects.filter(status_approve=True, date_from__lte=today, date_to__gte=today).values('user__id')
absent = Absent.objects.filter(absent_on=today).values('user__user__id')
class AbsentForm(forms.ModelForm):
    # user = NameChoiceField(queryset=Employee.objects.order_by('name').exclude(Q(user__id__in = absent) | Q(user__id__in = leave)))

    def __init__(self, com_id, *args, **kwargs):
        super(AbsentForm, self).__init__(*args, **kwargs)
        emails = Employee.objects.filter(com_id=com_id).values_list('email', flat=True)
        self.fields['user']     = NameChoiceField(queryset=Employee.objects.filter(com_id=com_id).order_by('name').exclude(Q(user__id__in = absent) | Q(user__id__in = leave)))

    class Meta:
        model = Absent
        fields = ['user']


# Backup Form
class BackupUploadForm(forms.ModelForm):
    class Meta:
        model = CompanyBackup
        fields = ['backup_file']