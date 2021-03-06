from django.conf.urls import url
from .views import register,register_handler,login,login_check,logout,user,address,order,verifycode,register_active

urlpatterns = [
    url(r'^register/', register,name='register'),
    url(r'^register_handler/',register_handler,name='register_handler'),
    url(r'^login/$',login,name='login'),
    url(r'^login_check/$',login_check,name='login_check'),
    url(r'^logout/$',logout,name='logout'),
    url(r'^user/$',user,name='user'),
    url(r'^address/',address,name='address'),
    url(r'^order/(?P<page>\d+)/$',order,name='order'),
    url(r'^verifycode/',verifycode,name='verifycode'),
    url(r'^active/(?P<token>.*)/$',register_active,name='active'),

]
