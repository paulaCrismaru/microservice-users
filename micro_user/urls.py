from django.conf.urls import include, url
from django.contrib import admin

from friends.urls import friends_urls
from groups.urls import groups_urls
from users.urls import user_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

urlpatterns.extend(user_urls)
urlpatterns.extend(friends_urls)
urlpatterns.extend(groups_urls)
