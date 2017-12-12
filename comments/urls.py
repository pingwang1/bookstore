from django.conf.urls import url
from .views import comment
urlpatterns = [
	url(r'^comment/(?P<books_id>\d+)/$',comment,name='comment'),
 ]
