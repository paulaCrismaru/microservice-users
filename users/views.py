from django.contrib.auth.models import User
from rest_framework import generics

from users import serializers as user_serializers
from users.permissions import NotIsAuthenticated


# /users/
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = user_serializers.UserSerializer
    permission_classes = (NotIsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return user_serializers.UserSerializer
        return user_serializers.CreateUserSerializer


# /users/<uuid>/
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = user_serializers.UserSerializer
    lookup_url_kwarg = 'uuid'


# /users/me/
class CurrentUserDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.MeSerializer
    lookup_field = None

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)
