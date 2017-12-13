from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

@shared_task
def send_active_email(token,username,email):
	'''发送激活邮件'''
	subject ='书城用户激活' #标题
	message =''
	sender = settings.EMAIL_FROM #发件人
	receiver = [email] #发件人列表
	html_message = '<a href="http://192.168.16.53:8000/users/active/%s/">http://192.168.16.53:8000/users/active/</a>'%token
	send_mail(subject,message,sender,receiver,html_message=html_message)
