"""celerymonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from monitor.views import workers_index
from django.contrib.auth.views import login, logout
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login,
        {'template_name': 'login.html'}, name='login'),
    url(r'^accounts/logout/$', logout, name='loginout'),
    url(r'^monitor/', include('monitor.urls')),
    url(r'^$', workers_index.as_view()),
    #url(r'^grappelli/', include('grappelli.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token),
]


try:
    from .extend_urls import extend_urlpatterns
    urlpatterns = urlpatterns + extend_urlpatterns
except ImportError:
    pass
