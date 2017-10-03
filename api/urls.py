from django.conf.urls import include, url

import views

app_name = 'api'

user_urls = [
    url(r'users/$',  views.users_list),
    url(r'users/create/$', views.create_user),
]

friends_urls = [
    url(r'friends/sent_requests/?(?P<uuid>[0-9a-f\-]*)/$', views.sent_requests),
    url(r'friends/friend_requests/?(?P<uuid>[0-9a-f\-]*)/$', views.received_requests),
    url(r'friends/$', views.get_friends),
]

urlpatterns = []
urlpatterns.extend(user_urls)
urlpatterns.extend(friends_urls)
