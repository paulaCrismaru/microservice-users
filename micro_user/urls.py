from django.conf.urls import include, url
from django.contrib import admin

from api.api_views import users as views_users


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^', include('api.urls')),
    url(r'^$', views_users.home)
]
