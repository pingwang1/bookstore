from django.conf.urls import url
from .views import index,detail

urlpatterns = [
    url(r'^index/', index,name='index'),
    url(r'^detail/(?P<book_id>\d+)/$',detail,name='detail'),
 ]
