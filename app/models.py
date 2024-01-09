from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
 
# Create your models here.

# Request LEAPSS Model
class AllRequest(models.Model):
    company_name = models.CharField(max_length=500, unique=True)
    website = models.CharField(max_length=500, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=500, unique=True) 
    telephone = models.CharField(max_length=500, unique=True)
    telephone1 = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=500)
    country = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    pincode = models.CharField(max_length=500)
    username = models.CharField(max_length=500, unique=True)
    approve_status = models.BooleanField(default=False)
    decline_status = models.BooleanField(default=False)
    active_status = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name
    
# Company Model
class Company(models.Model):
    name = models.CharField(max_length=500)
    email = models.EmailField(max_length=500,unique=True) 
    website = models.CharField(max_length=500)
    telephone = models.CharField(max_length=500)
    telephone1 = models.CharField(max_length=500, blank=True, null=True)
    telephone2 = models.CharField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=500)
    pincode = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=500)
    country = models.CharField(max_length=500)
    username = models.CharField(max_length=500,unique=True,default='admin')
    password = models.CharField(max_length=500, default='12345678')
    logo = models.ImageField(upload_to='images/', default='dummylogo.png')
    setup_completed = models.BooleanField(default=True) 
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

# Department Model
class Department(models.Model):
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    dep_code = models.CharField(max_length=50)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.department
    

# date of birth validator 
    
def validate_dob(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

    if age < 18:
        raise ValidationError(
            # _("%(value)s is not an even number"),
            _("Age should be greater than 18"),
            params={"value": value},
        )

# Employee Model
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    company_contact = models.CharField(max_length=100,null=True,blank=True)
    personal_contact = models.CharField(max_length=100)
    present_address = models.CharField(max_length=100,null=True,blank=True)
    permanent_address = models.CharField(max_length=100,null=True,blank=True)
    dob = models.DateField(validators=[validate_dob])
    doj = models.DateField()
    gender = models.CharField(max_length=20)
    email = models.EmailField(max_length=70,null=True,blank=True, unique=True)
    office_email = models.EmailField(max_length=70, unique=True)
    image = models.ImageField(upload_to='images/', default='user.png')
    status = models.BooleanField(default=True)
    designation = models.CharField(max_length=200)
    level = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    reporting = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    deactivate = models.CharField(max_length=5000, null=True, blank=True)
    activate = models.CharField(max_length=5000, null=True, blank=True)
    employee_setup_completed = models.BooleanField(default=True) 

    class Meta:
        unique_together = ('com_id', 'emp_id')

    def __str__(self):
        return self.emp_id

# Leave Policy
class LeavePolicy(models.Model):
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE, default=1)
    leavepolicy = models.CharField(max_length=50000)

# Privacy Policy
class PrivacyPolicy(models.Model):
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE, default=1)
    privacypolicy = models.CharField(max_length=50000)

# Terms & Conditions
class Terms(models.Model):
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE, default=1)
    terms = models.CharField(max_length=50000)

class Leave(models.Model):
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200)
    days = models.IntegerField()

    def __str__(self):
        return self.name
    
class Quote(models.Model): 
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE, default=1)
    quotes = models.TextField(max_length=5000) 
    tod_date = models.DateField(auto_now=True)
      
class Event(models.Model): 
    CATEGORY_CHOICES = [ ('Birthday', 'Birthday'), ('Public Holiday', 'Public Holiday'), ('Event', 'Event'), ('Others', 'Others'),]
    com_id = models.ForeignKey(Company, on_delete=models.CASCADE, default=1)
    visibility = models.BooleanField(default=False ) 
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()
    @property
    def get_event_description(self):
          
        des =Event.objects.get(id = self.id,description = self.description) 
        try:
            des =Event.objects.get(id = self.id,description = self.description)
            return des.description
        except:
            return False
     
    @property
    def get_html_url(self):
        url = reverse('event_edit', args=(self.id,))
        return f'<a href="{url}"> <span class ="options" style="  margin-top:1px;color:#707070;  " > <img class="img1"style="width:20px; height:20px;" src="../static/assets/img/edit.png" alt="edit"/> </span></a><br> '
    @property
    def deleteEvent(self):  
        urls = reverse('event_delete', args=(self.id,))
        return f'<br><a href="{urls}"> <span class ="options"id = "options"  > <img class="img2"style="width:20px; margin-top:10px;color:#707070;"src="../static/assets/img/delete.png" alt="delete" onclick="return confirm(\'Are You Sure?\')"/> </span></a>'
        # return f'<br><button id="primaryButton{cot}" href="{urls}" ></button>' 
        # return f'<br> <a data-bs-toggle="modal" data-bs-target="#sureModal"> <span class ="options" style="  margin-top:20px;color:#707070;" > <img class="img2"style="width:20px; margin-top:10px;color:#707070;"src="../static/assets/img/delete.png" alt="delete"/> </span></a><div class="modal fade" id="sureModal" tabindex="-1" aria-labelledby="sureModalLabel" aria-hidden="true"> <div class="modal-dialog"> <div class="modal-content"> <div class="modal-header"><h5 class="modal-title" id="sureModalLabel">Are you Sure?</h5></div> <div class="modal-footer"><button type="button" style="background-color:red;" class="btn btn-danger" data-bs-dismiss="modal">No</button><a href="{urls}" class="btn btn-primary">Yes</a></div></div></div></div>'
        # return f'<br><button hidden id="primaryButton" href="{urls}"></button><a data-bs-toggle="modal" data-bs-target="#sureModal"> <span class ="options" style="  margin-top:20px;color:#707070;" > <img class="img2"style="width:20px; margin-top:10px;color:#707070;"src="../static/assets/img/delete.png" alt="delete"/> </span></a><div class="modal fade" id="sureModal" tabindex="-1" aria-labelledby="sureModalLabel" aria-hidden="true"> <div class="modal-dialog"> <div class="modal-content"> <div class="modal-header"><h5 class="modal-title" id="sureModalLabel">Are you Sure?</h5></div> <div class="modal-footer"><button type="button" style="background-color:red;" class="btn btn-danger" data-bs-dismiss="modal">No</button><button type="button" id='"secondaryButton"' class="btn btn-primary" onclick="document.getElementById("primaryButton").click()">Yes</button></div></div></div></div>'
    
class LeaveApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apply_on = models.DateField(auto_now=True)
    category = models.ForeignKey(Leave, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    reason = models.CharField(max_length=250, blank=True)
    leave_count = models.IntegerField(null=True, blank=True)
    level0_reject = models.BooleanField(default=False)
    level0_approve = models.BooleanField(default=False)
    level0_comm =  models.CharField(max_length=100, blank=True)
    level1_reject = models.BooleanField(default=False)
    level1_approve = models.BooleanField(default=False)
    level1_comm =  models.CharField(max_length=100, blank=True)
    level2_reject = models.BooleanField(default=False)
    level2_approve = models.BooleanField(default=False)
    level2_comm =  models.CharField(max_length=100, blank=True)
    status_reject = models.BooleanField(default=False)
    status_approve = models.BooleanField(default=False)

    def __str__(self):
        return self.user.employee.name
 
        
# Absent List
class Absent(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    absent_on = models.DateField(auto_now=True)

    def __str__(self):
        return self.user.name
    
    
class FeedbackModel(models.Model):
    text        = models.TextField()
    company_id  = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    emp_id      = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    to_devs     = models.BooleanField(default=True)
    
    def __str__(self):
        return self.text
    

class Support(models.Model):
    text = models.TextField()
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    id = models.BigAutoField(primary_key=True)
    resolved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.text


class CompanyBackup(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    backup_file = models.FileField(upload_to='backups/')
    created_at = models.DateTimeField(auto_now_add=True)