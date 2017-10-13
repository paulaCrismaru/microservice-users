from django.conf.urls import url

from api.api_urls.users import user_urls
from api.api_views import views

app_name = 'api'


friends_urls = [
    url(r'friends/sent_requests/?(?P<uuid>[0-9a-f\-]*)/$', views.sent_requests),
    url(r'friends/friend_requests/?(?P<uuid>[0-9a-f\-]*)/$', views.received_requests),
    url(r'friends/$', views.get_friends),
]

groups_urls = [
    # url(r'groups/all/$', views.groups_all),
    url(r'groups/$', views.groups_all_in),
    url(r'groups/(?P<group_id>[0-9]{18})/$', views.action_group),
    url(r'group/$', views.create_group),
]

urlpatterns = []
urlpatterns.extend(user_urls)
urlpatterns.extend(friends_urls)
urlpatterns.extend(groups_urls)
