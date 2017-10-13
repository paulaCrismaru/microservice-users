from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ParseError, APIException, PermissionDenied, ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from api import utils
from api.api_serializers.serializers import *


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
            raise NotFound()
        serializer = FriendSerializer(username_list)
    return Response(serializer.data, status=200)


def accept_friend(user, uuid):
    try:
        friendship = Friendships.objects.get(uuid=uuid, receiver=user)
        serializer = FriendshipSerializer(friendship)
        if serializer.data.get('acceptance') is True:
            return ParseError(detail="Already friends")
        serializer.update(friendship, {'acceptance': True})
    except ObjectDoesNotExist:
        raise NotFound()
    return FriendshipSerializer(serializer.data)


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
            raise NotFound()
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


# @csrf_exempt
# @api_view(['GET', 'POST'])
# def user_profile(request, uuid):
#     if request.method == 'GET':
#
#         try:
#             uuid = utils.decode(uuid)
#             serializer = UserSerializer(User.objects.get(pk=uuid))
#         except (ObjectDoesNotExist, ValueError):
#             raise NotFound()
#         return Response(serializer.data, status=200)
#     elif request.method == 'POST':
#         if not uuid:
#             raise ParseError()
#         data = JSONParser().parse(request)
#         if data.get('action') == 'ADD':
#             current_user = request.user
#             try:
#                 user = User.objects.get(pk=utils.decode(uuid))
#             except (ObjectDoesNotExist, ValueError):
#                 raise NotFound()
#             try:
#                 Friendships.objects.get(sender=current_user, receiver=user)
#                 Friendships.objects.get(receiver=current_user, sender=user)
#             except ObjectDoesNotExist:
#                 raise APIException(detail="A request to/from this user already exists", code=304)
#             friendship = Friendships(sender=current_user, receiver=user)
#             serializer = FriendshipSerializer(friendship)
#             friendship.save()
#             return Response(data=serializer.data, status=200)


@api_view(['GET'])
def groups_all_in(request):
    user = request.user
    serializer = GroupSerializer(user.groups.all(), many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def groups_all(request):
    serializer = GroupSerializer(Group.objects.all(), many=True)
    return Response(serializer.data, status=200)


@api_view(['GET', 'POST'])
def action_group(request, group_id):
    user = request.user
    try:
        group = Group.objects.get(string_date=group_id)
        if group in user.groups.all():
            serializer = GroupDetailsSerializer(group, context={'request': request})
        else:
            # TODO: clarify why
            serializer = GroupSerializer(group, context={'request': request})
    except ObjectDoesNotExist:
        raise NotFound()
    if request.method == 'GET':
        return Response(serializer.data,status=200)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        supported_actions = {
            'add_user': add_user_in_group,
            'make_admin': make_user_admin,
            'remove_admin': remove_user_admin,
        }
        requested_actions = set(supported_actions).intersection(set(data))
        if requested_actions:
            response = {}
            for action_name in requested_actions:
                action = supported_actions[action_name]
                username = data[action_name]
                if not serializer.data.get('is_member'):
                    raise PermissionDenied(detail="You are not part of this group")
                kwargs = {
                    "username": username,
                    "group": group,
                    "user": user
                }
                action(**kwargs)
                response.update(GroupDetailsSerializer(group, context={'request': request}).data)
                return Response(response, status=200)


def remove_user(**kwargs):
    username = kwargs.get('username')
    group = kwargs.get('group')
    user = kwargs.get('user')
    check_is_admin(user, group)
    user_to_remove = check_user_in_group(username, group)
    group.user_set.remove(user_to_remove)
    group.save()


def check_is_admin(user, group):
    if user not in group.admins.all():
        raise PermissionDenied(detail="You are not an admin of this group")


def check_user_exists(username):
    try:
        return User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise APIException("User '{}' does not exist".format(username), code=400)


def check_user_in_group(username, group):
    user = check_user_exists(username)
    if user not in group.user_set.all():
        raise APIException("User '{}' is not in this group member".format(username), code=400)
    return user


def remove_user_admin(**kwargs):
    username = kwargs.get('username')
    group = kwargs.get('group')
    user = kwargs.get('user')
    check_is_admin(user, group)
    admin_to_remove = check_user_in_group(username)
    group.admins.remove(admin_to_remove)
    group.save()


def make_user_admin(**kwargs):
    username = kwargs.get('username')
    group = kwargs.get('group')
    user = kwargs.get('user')
    check_is_admin(user, group)
    admin_to_make = check_user_in_group(username, group)
    if admin_to_make in group.admins.all():
        raise APIException("User {}' already an admin".format(username), code=400)
    group.admins.add(admin_to_make)
    group.save()


def add_user_in_group(**kwargs):
    username = kwargs.get('username')
    group = kwargs.get('group')
    user_to_add = check_user_exists(username)
    if user_to_add in group.user_set.all():
        raise APIException("User '{}' already a group member".format(username), code=400)
    group.user_set.add(user_to_add)
    group.save()


@csrf_exempt
@api_view(['POST'])
def create_group(request):
    user = request.user
    data = JSONParser().parse(request)
    serializer = GroupDetailsSerializer(data=data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    group = serializer.save()
    group.admins.add(user)
    group.user_set.add(user)
    return Response(serializer.data, status=201)



