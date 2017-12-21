import re
import json

from django.shortcuts import render,redirect
from django.urls import reverse
from django_redis import get_redis_connection

from .models import Passport,Address
from books.models import Books
from order.models import OrderInfo,OrderGoods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from utils.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from users.tasks import send_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import HttpResponse
from django.core.paginator import Paginator
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
	print("debug0:",username,password,email)
	#进行数据校验
	p = Passport.objects.check_passport(username=username)
	print("debug1:",p)
	if p:
		return JsonResponse({'res': '用户名已存在'})

	if not all([username,password,email]):
		return JsonResponse({'res':'参数不能为空'})

	# 判断邮箱是否合法
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
		# 邮箱不合法
		return JsonResponse({'res': '邮箱不合法!'})
	#进行业务处理，添加一个账户
	passport =Passport.objects.add_one_passport(username,password,email)
	print("debug2:",passport)
	#生成激活的token itsdangrous
	serializer = Serializer(settings.SECRET_KEY,3600)
	token = serializer.dumps({'confirm':passport.id})
	print("debug3:",token)
	try:
	    token=token.decode()
	except Exception as e:
	    print("debug4:",e)
	print('123')
	#给用户的邮箱发送激活邮件
	#同步
	# send_mail('书城用户激活','',settings.EMAIL_FROM,[email],html_message='<a href="http://192.168.16.67:8000/users/active/%s/">http://192.168.16.67:8000/users/active/</a>'%token)

	#异步：使用redis celery 消息队列
	try:
	    send_active_email(token,username,email)
	except Exception as e:
	    print("debug5:",e)
	#注册后，返回到注册页面
	print("debug6:",111)
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
	verifycode=data.get('verifycode')
	#数据校验
	if verifycode.lower() !=request.session['verifycode']:
		return JsonResponse({'code':2})
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
	#获取用户的最近浏览信息
	con =get_redis_connection('default')
	key ='history_%d'%passport_id
	#取出用户最近浏览的５个商品的id
	history_li = con.lrange(key,0,4)
	book_li =[]
	for id in history_li:
		book = Books.objects.get_books_by_id(books_id=id)
		book_li.append(book)
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
def order(request,page):
	'''用户中心－订单页'''
	#查询用户的订单信息
	passport_id = request.session.get('passport_id')
	#获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)
	#分页
	paginator = Paginator(order_li,2)
	#获取分页后的总页数
	num_pages =paginator.num_pages
	#获取第page页是数据
	if page=='' or int(page) > num_pages:
		page =1
	else:
		page = int(page)
	# 返回值是一个Ｐａｇｅ类的实例对象
	order_li = paginator.page(page)
	# 进行页码控制
	# 1.总页数<5,显示所有页码
	# 2.当前页是前三页，显示１－５
	# 3.当前页是后３页，显示后５页
	# 4.其他情况，显示当前页前２页，后两页，当前页
	if num_pages <5:
		pages =range(1,num_pages+1)
	elif num_pages <3:
		pages = range(1,6)
	elif num_pages -page <=2:
		pages = range(num_pages-4,num_pages+1)
	else:
		pages=range(page-2,page+3)
	#遍历获取订单的商品信息
	#order->OrderInfo 实例对象
	for order in order_li:
		#根据订单id查询订单商品信息
		order_id = order.order_id
		order_books_li = OrderGoods.objects.filter(order_id=order_id)
		# order.status= OrderInfo.ORDER_STATUS_CHOICES[order.status-1][1]
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
		'page':'order',
		'pages':pages
	}
	return render(request,'users/user_center_order.html',context=context)


def verifycode(request):
	#引入绘图模式
	from PIL import Image,ImageDraw,ImageFont
	#引入随机函数模块
	import random
	#定义变量，用于画面的背景色，宽，高
	bgcolor = (random.randrange(20,100),random.randrange(20,100),255)
	width = 100
	height = 25
	#创建画面对象
	im = Image.new('RGB',(width,height),bgcolor)
	#创建画笔对象
	draw = ImageDraw.Draw(im)
	#调用画笔的point()函数绘制噪点
	for i in range(0,100):
		xy = (random.randrange(0,width),random.randrange(0,height))
		fill = (random.randrange(0,255),255,random.randrange(0,255))
		draw.point(xy,fill=fill)

	#定义验证码的备选值
	str1='1234567890qwertyuiopasdfghjklzxcvbnm'
	#随机选取４个值作为验证码
	rand_str=''
	for i in range(0,4):
		rand_str+=str1[random.randrange(0,len(str1))]
	#构造字体对象
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",15,encoding='unic')
	#构造字体颜色
	fontcolor = (255,random.randrange(0,255),random.randrange(0,255))
	#绘制４个字
	draw.text((5,2),rand_str[0],font=font,fill=fontcolor)
	draw.text((25,2),rand_str[1],font=font,fill=fill)
	draw.text((50,2),rand_str[2],font=font,fill=fill)
	draw.text((75,2),rand_str[3],font=font,fill=fill)

	#释放画笔
	del draw
	#存入session，用于做进一步的验证
	request.session['verifycode']=rand_str
	#内存文件操作
	import io
	buf = io.BytesIO()
	#将图片保存在内存中,文件类型为png
	im.save(buf,'png')
	#将内存中的图片数据返回给客户端，MIME类型为图片png
	return HttpResponse(buf.getvalue(),'image/png')


def register_active(request,token):
	'''用户账户激活'''
	serializer = Serializer(settings.SECRET_KEY,3600)
	try:
		info = serializer.loads(token)
		passport_id=info['confirm']
		#进行用户激活
		passport=Passport.objects.get(id=passport_id)
		passport.is_active=True
		passport.save()
		#跳转到登录页
		return redirect(reverse('users:login'))
	except SignatureExpired:
		#链接过期
		return HttpResponse('激活链接已过期')


