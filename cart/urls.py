from django.conf.urls import url
from .views import cart_add,cart_count,cart_show

urlpatterns = [
    url(r'^cart_add/', cart_add,name='cart_add'),
    url(r'^cart_count/',cart_count,name='cart_count'),
    url(r'^cart_show/',cart_show,name='cart_show'),
 ]
