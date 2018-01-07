from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response


from friends.models import Friendship
from friends import serializers as friends_serializers


# /friendships/requests/sent/
class RequestsSentList(generics.ListCreateAPIView):

    serializer_class = friends_serializers.CreateFriendshipSerializer

    def get_queryset(self):
        return Friendship.objects.filter(sender=self.request.user, acceptance=False)

    def create(self, request, *args, **kwargs):
        data = {
            'sender': self.request.user.pk,
            'receiver': request.data['receiver']
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        friendship = Friendship(**serializer.validated_data)
        friendship.sender = self.request.user
        friendship.save()


class RequestSent(generics.RetrieveDestroyAPIView):

    serializer_class = friends_serializers.CreateFriendshipSerializer
    queryset = Friendship.objects.all()


# /friendships/requests/
class Requests(generics.ListAPIView):

    serializer_class = friends_serializers.RequestDetailSerializer

    def get_queryset(self):
        return Friendship.objects.filter(receiver=self.request.user, acceptance=False)


# /friendships/requests/<pk>
class Request(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = friends_serializers.RequestDetailSerializer

    def get_queryset(self):
        return Friendship.objects.filter(receiver=self.request.user, acceptance=False)


# /friendships/
class FriendshipsList(generics.ListAPIView):

    serializer_class = friends_serializers.FriendSerializer

    def get_queryset(self):
        return Friendship.objects.filter(Q(sender__pk=self.request.user.pk)|Q(receiver__pk=self.request.user.pk),
                                         acceptance=True)


# /friendships/<pk>
class FriendshipDetails(generics.RetrieveDestroyAPIView):

    serializer_class = friends_serializers.FriendSerializer

    queryset = Friendship.objects.all()

    def get_queryset(self):
        return Friendship.objects.filter(Q(sender__pk=self.request.user.pk)|Q(receiver__pk=self.request.user.pk),
                                         acceptance=True, pk=self.kwargs['pk'])

    def get_serializer_context(self):
        return {'request': self.request}