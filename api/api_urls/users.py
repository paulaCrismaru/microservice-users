from django.conf.urls import url
from api.api_views import users as views_users


user_urls = [
    url(r'users/$', views_users.all_users),
    url(r'users/me/$', views_users.home),
    url(r'users/(?P<uuid>[0-9a-zA-Z]*)/$', views_users.user_profile),
]
