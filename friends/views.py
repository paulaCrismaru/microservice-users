from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response

from friends.models import Friendship
from friends import serializers as friends_serializers


# /friendships/<pk>/
class FriendshipDetails(generics.RetrieveUpdateDestroyAPIView):

    queryset = Friendship.objects.all()
    serializer_class = friends_serializers.FriendshipDetailSerializer


# /friendships/
class FriendshipsList(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = friends_serializers.FriendshipSerializer

    def get_queryset(self):
        if not self.request.query_params:
            return Friendship.objects.all()
        filter_dict = {}

        filter_type = self.request.query_params.get("request")
        if filter_type == "received":
            filter_dict['receiver__exact'] = self.request.user
        elif filter_type == "sent":
            filter_dict['sender__exact'] = self.request.user

        filter_type = self.request.query_params.get("accepted")
        if filter_type == "true":
            filter_dict['acceptance__exact'] = True
        elif filter_type == "false":
            filter_dict['acceptance__exact'] = False

        if filter_dict:
            return Friendship.objects.filter(**filter_dict)
        return Friendship.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        current_user = request.user
        try:
            user = get_object_or_404(User, pk=request_data.get('user_id'))
        except ValueError:
            raise NotFound()

        data = {
            "sender": current_user.pk,
            "receiver": user.pk
        }
        serializer = friends_serializers.FriendshipSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=201)


