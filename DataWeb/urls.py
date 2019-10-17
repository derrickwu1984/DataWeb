from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from download.views import show
from ftp.views import show_folder,index,file_Download

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^show/$',show),
    url(r'^folder/(?P<url>.+)/$', show_folder),
    url(r'^download/(?P<path>.+)/(?P<file>.+)/$', file_Download),
    url(r'^index/', index),

]
