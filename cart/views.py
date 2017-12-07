from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def cart_add(request):
	'''向购物车中添加数据'''
	#判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})
	#接收数据
	book_id = request.POST.get('book_id')
	book_count = request.POST.get('book_count')

	#进行数据校验




