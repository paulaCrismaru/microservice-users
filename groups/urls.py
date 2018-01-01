from django.conf.urls import url

from groups import views

app_name = 'groups'


groups_urls = [
    # url(r'groups/all/$', views.groups_all),
    # url(r'groups/?$', views.GroupsList.as_view()),
    url(r'groups/(?P<pk>[0-9]*)/members/?$', views.GroupMembers.as_view()),
    url(r'groups/(?P<pk>[0-9]*)/members/(?P<membership_id>[0-9]*)/?$', views.GroupMembersDetail.as_view()),
    url(r'groups/?$', views.GroupsList.as_view()),
    url(r'groups/(?P<pk>[0-9]*)/?$', views.GroupDetails.as_view()),

    # url(r'group/$', views.create_group),
]

urlpatterns = []
urlpatterns.extend(groups_urls)
