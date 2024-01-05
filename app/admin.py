from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Company)
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(LeavePolicy)
admin.site.register(Leave)
admin.site.register(LeaveApplication)
admin.site.register(Absent)
admin.site.register(Quote)
admin.site.register(AllRequest)
admin.site.register(PrivacyPolicy)
admin.site.register(Terms)
admin.site.register(CompanyBackup)
admin.site.register(FeedbackModel)