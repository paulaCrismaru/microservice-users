from django.conf.urls import url

from users import views as views_users

user_urls = [
    url(r'users/$', views_users.UserList.as_view()),
    url(r'users/me/$', views_users.CurrentUserDetails.as_view()),
    url(r'users/(?P<uuid>[0-9]*)/$', views_users.UserDetail.as_view()),
]
