from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users import serializers as user_serializers


# /users/
class UserList(mixins.ListModelMixin,
               generics.GenericAPIView):
    # TODO: fix warning
    # TODO: allow any only for create
    queryset = User.objects.all()
    serializer_class = user_serializers.UserSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        serializer = user_serializers.CreateUserSerializer(data=request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        new_user = serializer.save()
        return Response(user_serializers.UserSerializer(new_user).data, status=201)


# /users/<uuid>/
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = user_serializers.UserSerializer
    lookup_url_kwarg = 'uuid'


# /users/me/
class CurrentUserDetails(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = user_serializers.UserSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.request.user.pk)
        return obj


# @csrf_exempt
# @api_view(['GET'])
# def user_profile(request, uuid):
#     if request.method == 'GET':
#         try:
#             uuid = utils.decode(uuid)
#             serializer = user_serializers.UserSerializer(User.objects.get(pk=uuid))
#         except (ObjectDoesNotExist, ValueError):
#             raise NotFound()
#         return Response(serializer.data, status=200)
#     elif request.method == 'POST':
#         if not uuid:
#             raise ParseError()
#         data = request.data
#         if data.get('action') == 'ADD':
#             current_user = request.user
#             try:
#                 user = User.objects.get(pk=utils.decode(uuid))
#             except (ObjectDoesNotExist, ValueError):
#                 raise NotFound()
#             try:
#                 models.Friendships.objects.get(sender=current_user, receiver=user)
#                 models.Friendships.objects.get(receiver=current_user, sender=user)
#             except ObjectDoesNotExist:
#                 raise APIException(detail="A request to/from this user already exists", code=304)
#             friendship = models.Friendships(sender=current_user, receiver=user)
#             serializer = serializers.FriendshipSerializer(friendship)
#             friendship.save()
#             return Response(data=serializer.data, status=200)
