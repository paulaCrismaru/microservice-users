from django.conf.urls import include, url
from django.contrib import admin

from users import views as views_users
from users.urls import user_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^', include('api.urls')),
    # TODO: home
    url(r'^$', views_users.CurrentUserDetails.as_view())
]

urlpatterns.extend(user_urls)
