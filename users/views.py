import re
import json
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import Passport,Address
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from utils.decorators import login_required

# Create your views here.
def register(request):
	'''显示用户注册界面'''
	return render(request,'users/register.html')

@csrf_exempt
def register_handler(request):
	'''进行用户注册'''
	#接收数据
	print(request.body)
	data = json.loads(request.body.decode('utf-8'))
	username = data.get('username')
	password = data.get('password')
	email = data.get('email')
	print(username,password,email)
	#进行数据校验
	if not all([username,password,email]):
		# return render(request,'users/register.html',{'errormsg':'参数不能为空'})
		return JsonResponse({'res':'参数不能为空'})

	# 判断邮箱是否合法
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
		# 邮箱不合法
		# return render(request, 'users/register.html', {'errmsg': '邮箱不合法!'})
		return JsonResponse({'res': '邮箱不合法!'})
	#进行业务处理，添加一个账户(这里还没做去重，对用户名)
	passport =Passport.objects.add_one_passport(username,password,email)
	print(passport)
	#注册后，返回到注册页面
	# return redirect(reverse('users:login'))
	return JsonResponse({'res':1})

def login(request):
	# context={
	# 	'username':'',
	# 	'password':'',
	# }
	return render(request,'users/login.html')

@csrf_exempt
def login_check(request):
	print(request.body)
	data=json.loads(request.body.decode('utf-8'))
	username = data.get('username')
	password = data.get('password')
	# remember = data.get('remember')
	print(username,password)
	passport = Passport.objects.get_one_passport(username=username,password=password)
	print(passport)
	if passport:
		print("登录成功！")
		# 记住用户的登录状态
		request.session['islogin'] = True
		request.session['username'] = username
		request.session['passport_id'] = passport.id
		# return redirect(reverse('books:index'))
		return JsonResponse({'code':200})
	else:
		# p = Passport.objects.get_one_passport(username=username)
		# if not p:
		# 	return render(request,'users/login.html',{'errormsg':'用户名不存在'})
		# return render(request,'users/login.html',{'errormsg':'用户名或密码不正确'})
		return JsonResponse({'code':500})

def logout(request):
	request.session.flush()
	return redirect(reverse('books:index'))

#装饰器，需要登录才可以进入
@login_required
def user(request):
	'''用户中心－信息页'''
	passport_id = request.session.get('passport_id')
	#获取用户的基本信息
	addr = Address.objects.get_default_address(passport_id=passport_id)

	book_li =[]
	context = {
		'addr':addr,
		'page':'user',
		'book_li':book_li,
	}
	return render(request,'users/user_center_info.html',context)



