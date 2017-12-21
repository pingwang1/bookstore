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
	html_message = '<a href="http://47.93.227.58:8090/users/active/%s/">http://47.93.227.58:8090/users/active/</a>'%token
	send_mail(subject,message,sender,receiver,html_message=html_message)
