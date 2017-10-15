from django.conf.urls import url

from friends import views as views_friends

friends_urls = [

    url(r'friendships/?$', views_friends.FriendshipsList.as_view()),
    url(r'friendships/?(?P<pk>[0-9]*)/?$', views_friends.FriendshipDetails.as_view()),
]