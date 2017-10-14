from django.conf.urls import url
from api.api_views import friends as views_friends

friends_urls = [
    url(r'friends/sent_requests/?(?P<uuid>[0-9a-f\-]*)/$', views_friends.sent_requests),
    url(r'friends/friend_requests/?(?P<uuid>[0-9a-f\-]*)/$', views_friends.received_requests),
    url(r'friends/$', views_friends.friends),
]