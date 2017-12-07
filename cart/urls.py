from django.conf.urls import url
from .views import cart_add,cart_count

urlpatterns = [
    url(r'^cart_add/', cart_add,name='cart_add'),
    url(r'^cart_count/',cart_count,name='cart_count'),
 ]
