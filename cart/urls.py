from django.conf.urls import url
from .views import cart_add

urlpatterns = [
    url(r'^cart_add/', cart_add,name='cart_add'),
 ]
