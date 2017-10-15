from django.conf.urls import url

from api.api_views import views

app_name = 'api'


groups_urls = [
    # url(r'groups/all/$', views.groups_all),
    url(r'groups/$', views.groups_all_in),
    url(r'groups/(?P<group_id>[0-9]{18})/$', views.action_group),
    url(r'group/$', views.create_group),
]

urlpatterns = []
urlpatterns.extend(groups_urls)
