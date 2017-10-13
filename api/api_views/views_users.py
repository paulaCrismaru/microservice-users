from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ParseError, APIException, NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api import models
from api import utils
from api.api_serializers import serializers
from api.api_serializers import user_serializers


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def all_users(request):
    user = request.user
    if request.method == 'GET':
        if user.is_anonymous:
            return Response({"detail": NotAuthenticated.default_detail}, status=NotAuthenticated.status_code)
        serializer = user_serializers.UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data, status=200)
    elif request.method == 'POST':
        request_data = request.data
        serializer = user_serializers.CreateUserSerializer(data=request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        new_user = serializer.save()
        return Response(user_serializers.UserSerializer(new_user).data, status=201)


@csrf_exempt
@api_view(['GET', 'POST'])
def user_profile(request, uuid):
    if request.method == 'GET':
        try:
            uuid = utils.decode(uuid)
            serializer = user_serializers.UserSerializer(User.objects.get(pk=uuid))
        except (ObjectDoesNotExist, ValueError):
            raise NotFound()
        return Response(serializer.data, status=200)
    elif request.method == 'POST':
        if not uuid:
            raise ParseError()
        data = request.data
        if data.get('action') == 'ADD':
            current_user = request.user
            try:
                user = User.objects.get(pk=utils.decode(uuid))
            except (ObjectDoesNotExist, ValueError):
                raise NotFound()
            try:
                models.Friendships.objects.get(sender=current_user, receiver=user)
                models.Friendships.objects.get(receiver=current_user, sender=user)
            except ObjectDoesNotExist:
                raise APIException(detail="A request to/from this user already exists", code=304)
            friendship = models.Friendships(sender=current_user, receiver=user)
            serializer = serializers.FriendshipSerializer(friendship)
            friendship.save()
            return Response(data=serializer.data, status=200)


@api_view(['GET', 'DELETE'])
def home(request):
    user = request.user
    serializer = user_serializers.UserSerializer(user)
    if request.method == 'GET':
        pass
    elif request.method == 'DELETE':
        logout(request)
        user.delete()
    return Response(serializer.data, status=200)