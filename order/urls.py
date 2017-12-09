from django.conf.urls import url
from .views import order_place,order_commit

urlpatterns = [
    url(r'^order_place/', order_place,name='order_place'),
    url(r'^order_commit',order_commit,name='order_commit'),
]
