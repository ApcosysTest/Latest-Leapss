from django.core.mail import send_mail
from django.conf import settings

def send_account_creation_mail(office_email, name, company, username, password):
    subject = 'Account Created'
    message = f'Congratulations {name}, Your Acoount has been created in {company} under LEAPSS(Leave Application Software System).\n Username: {username} \n Password : {password}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [office_email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_company_login_credential_mail(company, username, password):
    subject = 'LEAPSS Credential Details'
    message = f'Company: {company}\n Username: {username} \n One Time Password : {password}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [username]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_otp_for_email_verification(otp, email):
    subject = 'LEAPSS Email Verification'
    message = f'One Time Password (OTP) : {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_admin_forgot_password_otp(otp, email):
    subject = 'Request For Password Change'
    message = f'One Time Password (OTP) : {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_mail_about_client_request(name):
    subject = 'Notification for Client Request'
    message = f'A new client request from {name} in leapss.com'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['mailbox101@apcosys.in']
    send_mail(subject, message, email_from, recipient_list)
    return True