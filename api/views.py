from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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


@api_view(['GET', 'DELETE'])
def sent_requests(request, uuid=None):
    user = request.user
    if request.method == 'GET':
        return get_sent_requests(user, uuid)
    elif request.method == 'DELETE':
        status = delete_friendship(uuid)
        return Response(status=status)


@api_view(['GET', 'DELETE'])
def received_requests(request, uuid=None):
    user = request.user
    if request.method == 'GET':
        return get_received_requests(user, uuid)
    elif request.method == 'DELETE':
        status = delete_friendship(uuid)
        return Response(status=status)


def action_user_friends(friend_type, **kwargs):
    if not kwargs.get('uuid__exact'):
        try:
            kwargs.pop('uuid__exact')
        except KeyError:
            pass
        user_list = Friendships.objects.filter(**kwargs)
        username_list = [{'username': f[friend_type]} for f in user_list]
        serializer = FriendSerializer(username_list, many=True)
    else:
        try:
            user_list = Friendships.objects.filter(**kwargs)
            username_list = {'username': user_list[0][friend_type]}
        except (IndexError, ValidationError):
            return Response(status=404)
        serializer = FriendSerializer(username_list)
    return Response(serializer.data, status=200)


def get_received_requests(user, uuid=None):
    kwargs = {
        'receiver__exact': user,
        'acceptance__exact': False
    }
    if uuid is not None:
        kwargs['uuid__exact'] = uuid
    return action_user_friends('sender', **kwargs)


def get_sent_requests(user, uuid=None):
    kwargs = {
        'sender__exact': user,
        'acceptance__exact': False
    }
    if uuid is not None:
        kwargs['uuid__exact'] = uuid
    return action_user_friends('receiver', **kwargs)


def delete_friendship(uuid):
    if uuid is not None:
        try:
            Friendships.objects.get(uuid=uuid).delete()
        except ObjectDoesNotExist:
            return 404
    return 200


@api_view(['GET'])
def get_friends(request):
    user = request.user
    friends_list = [{'username': f.receiver.username} for f in
                     Friendships.objects.filter((Q(receiver__exact=user) |
                                                Q(sender__exact=user)) &
                                                Q(acceptance__exact=True))]
    serializer = FriendSerializer(friends_list, many=True, context=request)
    return Response(serializer.data, status=200)
