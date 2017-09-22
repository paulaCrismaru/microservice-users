from rest_framework import routers
from django.conf.urls import include, url

import views

app_name = 'api'

# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)
urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'users/$',  views.users_list),
    url(r'users/create/$', views.create_user)
# url(r'^snippets/$', views.snippet_list),
]
