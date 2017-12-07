from django.conf.urls import url
from .views import index,detail,list

urlpatterns = [
    url(r'^index/', index,name='index'),
    url(r'^detail/(?P<book_id>\d+)/$',detail,name='detail'),
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$',list,name='list'),
 ]
