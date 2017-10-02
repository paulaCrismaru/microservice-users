from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from serializers import *
from models import Friendships


@api_view(['GET'])
def users_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def create_user(request):
    data = JSONParser().parse(request)
    serializer = CreateUserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def sent_requests(request):
    user = request.user
    username_list = [{'username': f.receiver.username} for f in Friendships.objects.filter(sender__exact=user, acceptance__exact=False)]
    serializer = FriendSerializer(username_list, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def received_requests(request):
    user = request.user
    username_list = [{'username': f.receiver.username} for f in
                     Friendships.objects.filter(receiver__exact=user, acceptance__exact=False)]
    serializer = FriendSerializer(username_list, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_friends(request):
    user = request.user
    friends_list = [{'username': f.receiver.username} for f in
                     Friendships.objects.filter((Q(receiver__exact=user) |
                                                Q(sender__exact=user)) &
                                                Q(acceptance__exact=True))]
    serializer = FriendSerializer(friends_list, many=True)
    return Response(serializer.data, status=200)
