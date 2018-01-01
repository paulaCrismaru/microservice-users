from django.conf.urls import include, url
from django.contrib import admin

from friends.urls import friends_urls
from users.urls import user_urls

from users import views as views_users

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^', include('groups.urls')),
    # TODO: home
    url(r'^$', views_users.CurrentUserDetails.as_view())
]

urlpatterns.extend(user_urls)
urlpatterns.extend(friends_urls)
