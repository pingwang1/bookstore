from django.conf.urls import url
from .views import cart_add,cart_count,cart_show,cart_del,cart_update

urlpatterns = [
    url(r'^cart_add/', cart_add,name='cart_add'),
    url(r'^cart_count/',cart_count,name='cart_count'),
    url(r'^cart_show/',cart_show,name='cart_show'),
	url(r'^cart_del/',cart_del,name='cart_del'),
	url(r'^cart_update/',cart_update,name='cart_update'),
 ]
