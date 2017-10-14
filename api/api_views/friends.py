from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ParseError, ValidationError, APIException
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from api.api_serializers import friends as friends_serializers
from api import models
from api import utils


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
    if status == 404:
        raise NotFound()
    return Response(status=status)


def action_user_interaction(friend_type, **kwargs):
    serializer_class = kwargs.pop('serializer')
    if not kwargs.get('uuid__exact'):
        try:
            kwargs.pop('uuid__exact')
        except KeyError:
            pass
        friendship_list = models.Friendships.objects.filter(**kwargs)
        serializer = serializer_class(friendship_list, many=True)
    else:
        try:
            friendship_list = models.Friendships.objects.filter(**kwargs)
        except (IndexError, ValidationError):
            raise NotFound()
        serializer = serializer_class(friendship_list)
    return Response(serializer.data, status=200)


def accept_friend(user, uuid):
    try:
        friendship = models.Friendships.objects.get(uuid=uuid, receiver=user)
        serializer = friends_serializers.FriendshipSerializer(friendship)
        if serializer.data.get('acceptance') is True:
            return ParseError(detail="Already friends")
        serializer.update(friendship, {'acceptance': True})
    except ObjectDoesNotExist:
        raise NotFound()
    return friends_serializers.FriendshipSerializer(serializer.data)


def get_received_requests(user, uuid=None):
    kwargs = {
        'receiver__exact': user,
        'acceptance__exact': False,
        'serializer': friends_serializers.ReceiverSerializer
    }
    if uuid is not None:
        kwargs['uuid__exact'] = uuid
    return action_user_interaction('sender', **kwargs)


def get_sent_requests(user, uuid=None):
    kwargs = {
        'sender__exact': user,
        'acceptance__exact': False,
        'serializer': friends_serializers.SenderSerializer
    }
    if uuid is not None:
        kwargs['uuid__exact'] = uuid
    return action_user_interaction('receiver', **kwargs)


def delete_friendship(uuid):
    if uuid is not None:
        try:
            friends_serializers.Friendships.objects.get(uuid=uuid).delete()
        except ObjectDoesNotExist:
            raise NotFound()
    return 200


@csrf_exempt
@api_view(['GET', 'POST'])
def friends(request):
    if request.method == 'GET':
        user = request.user
        friends_list = [{'username': f.receiver.username} for f in
                        friends_serializers.Friendships.objects.filter(Q(sender__exact=user)&
                                                   Q(acceptance__exact=True))]
        friends_list.extend([{'username': f.sender.username} for f in
                             friends_serializers.Friendships.objects.filter(Q(receiver__exact=user)&
                                                       Q(acceptance__exact=True))])
        serializer = friends_serializers.FriendSerializer(friends_list, many=True, context=request)
        return Response({"friends": serializer.data}, status=200)
    elif request.method == 'POST':
        data = request.data
        if data.get('action') == 'ADD':
            current_user = request.user
            uuid = data.get('user_id')
            try:
                user = User.objects.get(pk=utils.decode(uuid))
            except (ObjectDoesNotExist, ValueError):
                raise NotFound()
            try:
                models.Friendships.objects.get(sender=current_user, receiver=user)
            except ObjectDoesNotExist:
                pass
            else:
                raise ValidationError(detail="A request to/from this user already exists")
            try:
                models.Friendships.objects.get(receiver=current_user, sender=user)
            except ObjectDoesNotExist:
                pass
            else:
                raise ValidationError(detail="A request to/from this user already exists")
            friendship = models.Friendships(sender=current_user, receiver=user)
            serializer = friends_serializers.FriendshipSerializer(friendship)
            friendship.save()
            return Response(data=serializer.data, status=201)
        return ParseError()