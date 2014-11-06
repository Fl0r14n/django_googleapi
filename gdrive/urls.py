from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

import views


urlpatterns = patterns(
    'gauth',
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^login/$', logout, {'template_name': 'logout.html'}, name='logout'),
    url(r'^oauth2_begin/$', views.oauth2_begin, name='oauth2_begin'),
    url(r'^' + settings.OAUTH2_CALLBACK + '/$', views.oauth2_callback),
    url(r'^oauth2_complete/$', views.oauth2_complete, name='oauth2_complete'),

)
