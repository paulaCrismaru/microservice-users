from django.conf.urls import url

from friends import views as views_friends

friends_urls = [
    url(r'^friendships/?$', views_friends.FriendshipsList.as_view()),
    url(r'^friendships/(?P<pk>[0-9]*)/?$', views_friends.FriendshipDetails.as_view()),
    url(r'^friendships/requests/?$', views_friends.Requests.as_view()),
    url(r'^friendships/requests/(?P<pk>[0-9]*)/?$', views_friends.Request.as_view()),
    url(r'^friendships/requests/sent/?$', views_friends.RequestsSentList.as_view()),
    url(r'^friendships/requests/sent/(?P<pk>[0-9]*)/?$', views_friends.RequestSent.as_view()),


]