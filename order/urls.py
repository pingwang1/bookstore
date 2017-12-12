from django.conf.urls import url
from .views import order_place,order_commit,order_pay,check_pay

urlpatterns = [
    url(r'^order_place/', order_place,name='order_place'),
    url(r'^order_commit',order_commit,name='order_commit'),
    url(r'^order_pay/',order_pay,name='order_pay'),
    url(r'^check_pay/',check_pay,name='check_pay'),
]
