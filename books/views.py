from django.shortcuts import render,redirect
from django_redis import get_redis_connection

from books.models import Books
from books.enums import *
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.cache import cache_page


# Create your views here.
# @cache_page(60*2)
def index(request):
	'''显示首页'''
	#查询每个种类的３个新品信息和４个销量最好的商品信息
	python_new = Books.objects.get_books_by_type(PYTHON,3,sort='new')
	python_hot = Books.objects.get_books_by_type(PYTHON,4,sort='hot')
	javascript_new = Books.objects.get_books_by_type(JAVASCRIPT,3,sort='new')
	javascript_hot=Books.objects.get_books_by_type(JAVASCRIPT,4,sort='hot')
	algorithms_new=Books.objects.get_books_by_type(ALGORITHMS,3,sort='new')
	algorithms_hot=Books.objects.get_books_by_type(ALGORITHMS,4,sort='hot')
	machinelearning_new=Books.objects.get_books_by_type(MACHINELEARNING,3,sort='new')
	machinelearning_hot =Books.objects.get_books_by_type(MACHINELEARNING,4,sort='hot')
	operatingsystem_new = Books.objects.get_books_by_type(OPERATINGSYSTEM,3,sort='new')
	operatingsystem_hot =Books.objects.get_books_by_type(OPERATINGSYSTEM,4,sort='hot')
	database_new = Books.objects.get_books_by_type(DATABASE,3,sort='new')
	database_hot = Books.objects.get_books_by_type(DATABASE,4,sort='hot')
	#定义模板上下文
	context={
		'python_new':python_new,
		'python_hot':python_hot,
		'javascript_new':javascript_new,
		'javascript_hot':javascript_hot,
		'algorithms_new':algorithms_new,
		'algorithms_hot':algorithms_hot,
		'machinelearning_new':machinelearning_new,
		'machinelearning_hot':machinelearning_hot,
		'operatingsystem_new':operatingsystem_new,
		'operatingsystem_hot':operatingsystem_hot,
		'database_new':database_new,
		'database_hot':database_hot,
	}
	#使用模板
	return render(request,'books/index.html',context)

def detail(request,book_id):
	'''显示商品的详情页面'''
	#获取商品的详情信息
	book = Books.objects.get_books_by_id(books_id=book_id)
	print(book.name,book.price,book.desc,book.detail)
	if book is None:
		#商品不存在，跳转到首页
		return redirect(reverse('books:index'))
	book_new=Books.objects.get_books_by_type(type_id=book.type_id,limit=2)
	#用户和登录之后，才记录浏览记录
	#每个用户浏览记录对应redis中的一条信息，格式：history_用户id:[10,9,2,3,4]
	#[9,10,2,3,4]
	if request.session.has_key('islogin'):
		#用户已登录，记录浏览记录
		con = get_redis_connection('default')
		key = 'history_%d'%request.session.get('passport_id')
		#先从redis列表中移除book.id
		con.lrem(key,0,book_id)
		con.lpush(key,book_id)
		#保存用户最近浏览的５个商品
		con.ltrim(key,0,4)
	context={
		'book':book,
		'book_new':book_new,

	}
	# return JsonResponse({'code':200})
	return render(request,'books/detail.html',context)

# 商品种类 页码 排序方式
# /list/(种类id)/(页码)/?sort=排序方式
def list(request,type_id,page):
	'''商品列表的页面'''
	print(type_id,page)
	#获取排序方式
	sort = request.GET.get('sort','default')
	#判断type_id是否合法
	if int(type_id) not in BOOKS_TYPE.keys():
		return redirect(reverse('books:index'))
	#根据商品种类id和排序方式查询数据
	book_li = Books.objects.get_books_by_type(type_id=type_id,sort=sort)
	#分页
	paginator = Paginator(book_li,1)
	#获取分页之后的总页数
	num_pages = paginator.num_pages
	#获取第page页的数据
	if page=='' or int(page) >num_pages:
		page = 1
	else:
		page = int(page)
	#返回值是一个Ｐａｇｅ类的实例对象
	book_li = paginator.page(page)
	#进行页码控制
	#1.总页数<5,显示所有页码
	#2.当前页是前三页，显示１－５
	#3.当前页是后３页，显示后５页
	#4.其他情况，显示当前页前２页，后两页，当前页
	if num_pages <5:
		pages = range(1,num_pages+1)
	elif page <=3:
		pages = range(1,6)
	elif num_pages-page<=2:
		pages = range(num_pages-4,num_pages+1)
	else:
		pages = range(page-2,page+3)
	#新品
	book_new=Books.objects.get_books_by_type(type_id=type_id,limit=2,sort='new')
	#获取类型
	type_title=BOOKS_TYPE[int(type_id)]
	context={
		'book_li':book_li,
		'book_new':book_new,
		'type_id': type_id,
		'sort':sort,
		'type_title':type_title,
		'pages':pages
	}
	return render(request,'books/list.html',context=context)