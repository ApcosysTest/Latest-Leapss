 
from django.contrib import admin
from django.urls import path , re_path
from app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.conf import settings # new
from  django.conf.urls.static import static #new

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landingpage, name='landingpage'),
    path('homepage', homepage, name='homepage'),
    path('logout',LogoutView.as_view(next_page='/'),name='logout'),

    # Apply LEAPSS
    path('requestApplication', requestApplication, name='requestApplication'), 
    path('successfullyApply', successfullyApply, name='successfullyApply'), 
    path('appRequestDashboard', appRequestDashboard, name='appRequestDashboard'), 
    path('approvedClientDashboard', approvedClientDashboard, name='approvedClientDashboard'),
    path('inactiveClientDashboard', inactiveClientDashboard, name='inactiveClientDashboard'), 
    path('activeClientDashboard', activeClientDashboard, name='activeClientDashboard'), 
    path('rejectedClientDashboard', rejectedClientDashboard, name='rejectedClientDashboard'), 
    path('ApproveClient/<int:client_id>/', ApproveClient, name='ApproveClient'), 
    path('RejectClient/<int:client_id>/', RejectClient, name='RejectClient'), 
    path('undoClient/<int:client_id>/', undoClient, name='undoClient'), 
    path('enableClient/<int:client_id>/', enableClient, name='enableClient'), 
    path('disableClient/<int:client_id>/', disableClient, name='disableClient'), 
    path('viewClient/<int:client_id>/', viewClient, name='viewClient'), 
    path('companyLogin', companyLogin, name='companyLogin'), 
    path('newCompanySetup/<str:otp>/<str:username>/', newCompanySetup, name='newCompanySetup'), 
    path('appDisabled', appDisabled, name='appDisabled'), 
    path('homeDashboard/', homeDashboard, name='homeDashboard'), 
    path('getDashboardData/<int:client_id>/', getDashboardData, name='getDashboardData'), 
    path('superadminlogin', superadminlogin, name='superadminlogin'),
    path('logout_superuser', logout_superuser, name='logout_superuser'),

    
    path('employeereport', employeereport, name='employeereport'), 
    path('leavereport', leavereport, name='leavereport'), 

    path('companyfeedback', companyfeedback, name='companyfeedback'),
    path('employeefeedback', employeefeedback, name='employeefeedback'),
    path('viewfeedbackClient/<int:feedback_id>/', viewfeedbackClient, name='viewfeedbackClient'),
    path('viewemployeefeedbackClient/<int:feedback_id>/', viewemployeefeedbackClient, name='viewemployeefeedbackClient'), 


    # Admin
    # path('adminLogin', adminLogin, name='adminLogin'), 
    re_path(r'^adminDashboard$', CalendarView.as_view(), name='adminDashboard'), 
    re_path(r'^event/new$', event ,name='event_new'),
    re_path(r'^event/delete/(?P<event_id>\d+)/$', delete_event, name='event_delete'),
    re_path(r'^event/edit/(?P<event_id>\d+)/$', event , name='event_edit'),
    path('totalEmployees', totalEmployees, name="totalEmployees"),
    path('onLeave', onLeave, name='onLeave'),
    path('<int:id>/deleteAbsent', deleteAbsent, name='deleteAbsent'),
    path('<int:id>/totalEmployeeDetails', totalEmployeeDetails, name='totalEmployeeDetails'),
    path('activeEmployee', activeEmployee, name='activeEmployee'),
    path('<int:id>/deactivateDetail',deactivateDetail, name='deactivateDetail'),
    path('inactiveEmployee', inactiveEmployee, name='inactiveEmployee'),
    path('allactiveEmployee', allactiveEmployee, name='allactiveEmployee'),
    path('<int:id>/activateDetail',activateDetail, name='activateDetail'),
    path('addEmployee',addEmployee, name='addEmployee'),
    path('addEmployeebyExcel',addEmployeebyExcel, name='addEmployeebyExcel'),
    path('download_employees', download_employees_as_excel, name='download_employees'),
    path('<int:id>/viewEmployee',viewEmployee, name='viewEmployee'),
    path('<int:id>/editEmployee',editEmployee, name='editEmployee'),
    path('<int:id>/changePassword',changePassword, name='changePassword'),
    path('companySetup', companySetup, name='companySetup'),
    path('<int:id>/editCompany', editCompany, name='editCompany'),
    path('department', department, name='department'),
    path('addDepartment', addDepartment, name='addDepartment'),
    path('<int:id>/editDepartment', editDepartment, name='editDepartment'),
    path('<int:id>/deleteDepartment', deleteDepartment, name='deleteDepartment'),
    path('leaveApplicationDetails', leaveApplicationDetails, name='leaveApplicationDetails'),
    path('<int:id>/reviewEmployeeApplication', reviewEmployeeApplication, name='reviewEmployeeApplication'),
    path("<int:id>/approveLeaveAdmin", approveLeaveAdmin, name='approveLeaveAdmin'),
    path("<int:id>/rejectLeaveAdmin", rejectLeaveAdmin, name='rejectLeaveAdmin'),
    path("adminForgotPassword", adminForgotPassword, name='adminForgotPassword'),
    path('changeAdminPassword/<str:email>/', changeAdminPassword, name='changeAdminPassword'),
    path('setupPrivacyPolicy', setupPrivacyPolicy, name='setupPrivacyPolicy'),
    path('setupTandC', setupTandC, name='setupTandC'),
    path('feedback', feedback, name='feedback'),
    path('feedback_emp', feedback_emp, name='feedback_emp'),
    path('supportcompany', supportcompany, name='supportcompany'),

    path('admincompanysupport', admincompanysupport, name='admincompanysupport'),
    path('viewsupportClient/<int:support_id>/', viewsupportClient, name='viewsupportClient'),
    path('queryresolve/<int:id>/', queryresolve, name='queryresolve'),
    path('queryraise/<int:id>/', queryraise, name='queryraise'),
    path('viewquery/<int:id>/', viewquery, name='viewquery'),
    path('querycomment/<int:id>/', querycomment, name='querycomment'),
   
    



    
    path('reportPrinting', reportPrinting, name='reportPrinting'),
    path('download_pdf_report/<str:option>/', download_pdf_report, name='download_pdf_report'),
    path('generate_employee_report', generate_employee_report, name='generate_employee_report'),
    path('download_event_report/<str:option>/', download_event_report, name='download_event_report'),
    path('download_leave_report/<str:option>/', download_leave_report, name='download_leave_report'),
    path('generate_employee_leave_report', generate_employee_leave_report, name='generate_employee_leave_report'),

    path('backups/', backup_list, name='backup_list'),
    path('create_backup/', create_backup, name='create_backup'),
    path('upload_backup/', upload_backup, name='upload_backup'),
    path('retrieve_backup/', retrieve_backup, name='retrieve_backup'),



# Employee
    path('employeeLogin', employeeLogin, name='employeeLogin'),
    path('employeeSetupInitialization/<str:email>', employeeSetupInitialization, name='employeeSetupInitialization'),
    re_path(r'^sidebar$', CalendarViewEmp.as_view(), name='sidebar'),
    path('profileSetting', profileSetting, name='profileSetting'),
    path('howToUse', howToUse, name='howToUse'),
    path('leaveSection', leaveSection, name='leaveSection'),
    path('leaveApplication', leaveApplication, name='leaveApplication'),
    path('withdrawLeaveApplication/<int:id>', withdrawLeaveApplication, name='withdrawLeaveApplication'),
    path('leavePolicy', leavePolicy, name='leavePolicy'),
    path('privacyPolicy', privacyPolicy, name='privacyPolicy'),
    path('termsAndConditions', termsAndConditions, name='termsAndConditions'),
    path('leaveBasket', leaveBasket, name='leaveBasket'),
    path('leaveBasketAdmin/<int:id>', leaveBasketAdmin, name='leaveBasketAdmin'),
    path("approvalStatus",approvalStatus, name='approvalStatus'),
    path('presentEmployees', presentEmployees, name='presentEmployees'),
    path('reviewEmployeeApplicationEmployee/<int:id>', reviewEmployeeApplicationEmployee, name='reviewEmployeeApplicationEmployee'), 

    path('check_email_uniqueness', check_email_uniqueness, name='check_email_uniqueness'),

    # Employee Level 0
    # re_path(r'^hrAdminDashboard$', CalendarViewHR.as_view(), name='hrAdminDashboard'), 


    # Employee Level 1 & 2
    path("leaveStatus",leaveStatus, name='leaveStatus'),
    path("<int:id>/reviewLeaveApplication", reviewLeaveApplication, name='reviewLeaveApplication'),
    path("<int:id>/approveLeave", approveLeave, name='approveLeave'),
    path("<int:id>/rejectLeave", rejectLeave, name='rejectLeave'), 
    path('leaveapplications', leaveapplications),  
    path('reviewEmployeeApplication/<str:Emp_ID>/<int:id>', reviewEmployeeApplication),  
    path('prev_month', prev_month, name='prev_month'),
    path('next_month', next_month, name='next_month'),   
    path('howToUse', howToUse, name='howToUse'),
    path('leavePolicy', leavePolicy, name='leavePolicy'),
    path('leavePolicySetting', leavePolicySetting, name='leavePolicySetting'),
    path('addLeave', addLeave, name='addLeave'),
    path('<int:id>/editLeave',editLeave, name='editLeave'),
    path('<int:id>/deleteLeave',deleteLeave, name='deleteLeave'),

]
 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
elif getattr(settings, 'FORCE_SERVE_STATIC', False):
    settings.DEBUG = True
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    settings.DEBUG = False
