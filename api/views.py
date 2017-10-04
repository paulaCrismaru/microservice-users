from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from serializers import *
from models import Friendships
import utils


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
    try:
        serializer = CreateUserSerializer()
        serializer.create(data)
    except ValidationError as exception:
        return Response(exception.messages, status=400)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'DELETE'])
def sent_requests(request, uuid=None):
    user = request.user
    if request.method == 'GET':
        return get_sent_requests(user, uuid)
    elif request.method == 'DELETE':
        status = delete_friendship(uuid)
        return Response(status=status)


@csrf_exempt
@api_view(['GET', 'DELETE', 'POST'])
def received_requests(request, uuid=None):
    user = request.user
    status = 404
    if request.method == 'GET':
        return get_received_requests(user, uuid)
    elif request.method == 'DELETE':
        status = delete_friendship(uuid)
    elif request.method == 'POST':
        if uuid is not None:
            data = JSONParser().parse(request)
            if data.get('action') == 'accept':
                status = accept_friend(user, uuid)
            elif data.get('action') in ['ignore', 'delete']:
                status = delete_friendship(uuid)
    return Response(status=status)


def action_user_interaction(friend_type, **kwargs):
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


def accept_friend(user, uuid):
    try:
        friendship = Friendships.objects.get(uuid=uuid, receiver=user)
        if friendship.acceptance is True:
            return 403
        friendship.acceptance = True
        friendship.save()
    except ObjectDoesNotExist:
        return 404
    return 200


def get_received_requests(user, uuid=None):
    kwargs = {
        'receiver__exact': user,
        'acceptance__exact': False
    }
    if uuid is not None:
        kwargs['uuid__exact'] = uuid
    return action_user_interaction('sender', **kwargs)


def get_sent_requests(user, uuid=None):
    kwargs = {
        'sender__exact': user,
        'acceptance__exact': False
    }
    if uuid is not None:
        kwargs['uuid__exact'] = uuid
    return action_user_interaction('receiver', **kwargs)


def delete_friendship(uuid):
    if uuid is not None:
        try:
            Friendships.objects.get(uuid=uuid).delete()
        except ObjectDoesNotExist:
            return 404
    return 200


@csrf_exempt
@api_view(['GET'])
def get_friends(request):
    user = request.user
    friends_list = [{'username': f.receiver.username} for f in
                    Friendships.objects.filter(Q(sender__exact=user)&
                                               Q(acceptance__exact=True))]
    friends_list.extend([{'username': f.sender.username} for f in
                        Friendships.objects.filter(Q(receiver__exact=user)&
                                                   Q(acceptance__exact=True))])
    serializer = FriendSerializer(friends_list, many=True, context=request)
    return Response(serializer.data, status=200)


@csrf_exempt
@api_view(['GET'])
def user_profile(request, uuid=None):
    if uuid is None:
        # return current user profile
        pass
    else:
        uuid = utils.decode(uuid)
        try:
            serializer = UserSerializer(User.objects.get(pk=uuid))
        except ObjectDoesNotExist:
            return Response(status=404)
        return Response(serializer.data, status=200)
