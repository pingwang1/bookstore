import re
import json

from django.shortcuts import render,redirect
from django.urls import reverse
from .models import Passport,Address
from order.models import OrderInfo,OrderGoods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from utils.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
#itsdangerous 是一个产生token的库，有flask的作者编写

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
	#进行数据校验
	p = Passport.objects.check_passport(username=username)
	print('==============')
	if p:
		return JsonResponse({'res': '用户名已存在'})

	if not all([username,password,email]):
		return JsonResponse({'res':'参数不能为空'})

	# 判断邮箱是否合法
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
		# 邮箱不合法
		return JsonResponse({'res': '邮箱不合法!'})
	#进行业务处理，添加一个账户(这里还没做去重，对用户名)
	passport =Passport.objects.add_one_passport(username,password,email)
	print(passport)
	#生成激活的token itsdangrous
	serializer = Serializer(settings.SECRET_KEY,3600)
	token = serializer.dumps({'comfirm':passport.id})
	print(token)
	token=token.decode()
	#给用户的邮箱发送激活邮件
	send_mail('书城用户激活','',settings.EMAIL_FROM,[email],html_message='<a href="http://192.168.16.67:8000/users/active/%s/">http://192.168.16.67:8000/users/active/</a>'%token)
	#注册后，返回到注册页面
	# return redirect(reverse('books:index'))
	return JsonResponse({'res':1})

def login(request):
	'''显示登录页面'''
	context={
		'username':'',
		'checked':'',
	}
	return render(request,'users/login.html',context)

@csrf_exempt
def login_check(request):
	data=json.loads(request.body.decode('utf-8'))
	username = data.get('username')
	password = data.get('password')
	remember = data.get('remember')
	passport = Passport.objects.get_one_passport(username=username,password=password)
	jres = JsonResponse({'code':200})
	if passport:
		print("登录成功！")
		# 记住用户的登录状态
		print(remember,type(remember))
		if remember:
			#记住用户名
			jres.set_cookie('username',username,max_age=7*24*3600)
		else:
			#不记住
			jres.delete_cookie('username')
		request.session['islogin'] = True
		request.session['username'] = username
		request.session['passport_id'] = passport.id

		# return redirect(reverse('books:index'))
		return jres
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

@login_required
def address(request):
	'''用户中心－地址页'''
	#获取登录用户的id
	passport_id=request.session.get('passport_id')
	if request.method=='GET':
		#显示地址页面
		#查询用户的默认地址
		addr = Address.objects.get_default_address(passport_id=passport_id)
		return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})
	else:
		#添加收货地址
		#1.接收数据
		recipient_name = request.POST.get('username')
		recipient_addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		recipient_phone = request.POST.get('phone')
		print(111)
		#2.进行校验
		if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
			return render(request,'users/user_center_site.html',{'errmsg':'参数不全'})

		#3.添加收货地址
		Address.objects.add_one_address(passport_id=passport_id,
										recipient_name=recipient_name,
										recipient_addr=recipient_addr,
										zip_code=zip_code,
										recipient_phone=recipient_phone)
		#4.返回应答
		return redirect(reverse('users:address'))

@login_required
def order(request):
	'''用户中心－订单页'''
	#查询用户的订单信息
	passport_id = request.session.get('passport_id')
	#获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)
	#遍历获取订单的商品信息
	#order->OrderInfo 实例对象
	for order in order_li:
		#根据订单id查询订单商品信息
		order_id = order.order_id
		order_books_li = OrderGoods.objects.filter(order_id=order_id)
		order.status= OrderInfo.ORDER_STATUS_CHOICES[order.status-1][1]

		#计算商品的小计
		#order_books - >OrderGoods实例对象
		for order_books in order_books_li:
			count = order_books.count
			price = order_books.price
			amount = count*price
			#保存订单中每一个商品的小计
			order_books.amount =amount

		#给order对象动态增加一个属性order_books_li,保存订单中商品的信息
		order.order_books_li=order_books_li

	context ={
		'order_li':order_li,
		'page':'order'
	}
	return render(request,'users/user_center_order.html',context=context)


