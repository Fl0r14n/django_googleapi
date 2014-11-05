from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

import views

urlpatterns = patterns(
    'gauth',
    url(r'^login/$', login, {'template_name': 'login.html'}),
    url(r'^login/$', logout, {'template_name': 'logout.html'}),
    url(r'^begin/$', views.begin, name='begin'),
    url(r'^oauth2callback/$', views.complete, name='complete'),
)
