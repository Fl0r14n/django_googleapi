from django.conf.urls import patterns, include, url
from django.contrib import admin
import gdrive.urls
from gdrive.views import index


urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(gdrive.urls)),
)
