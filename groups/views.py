from django.db import IntegrityError
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework import generics, status

from groups.models import Membership
from groups.serializers import GroupDetailsSerializer, GroupSerializer, CreateMembershipSerializer,\
    MembershipSerializer, MemberSerializer


class GroupsList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        group = serializer.save()
        membership_serializer = CreateMembershipSerializer(data={'group': group.pk, 'person': user.pk, 'admin': True})
        if not membership_serializer.is_valid():
            return Response(membership_serializer.errors, status=400)
        membership_serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupDetails(generics.RetrieveUpdateDestroyAPIView):

    queryset = Group.objects.all()
    serializer_class = GroupDetailsSerializer


class GroupMembers(generics.ListCreateAPIView):

    serializer_class = MembershipSerializer

    def get_queryset(self):
        group_id = self.kwargs['pk']
        return Membership.objects.filter(group__id=group_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_name = serializer.validated_data['person']
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return Response("User {} is already part of the group".format(user_name),
                            status=status.HTTP_204_NO_CONTENT)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        m = Membership(**serializer.validated_data)
        group_id = self.kwargs['pk']
        m.group = Group.objects.get(pk=group_id)
        m.save()


class GroupMembersDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = MemberSerializer
    lookup_url_kwarg = "membership_id"

    def get_queryset(self):
        membership_id = self.kwargs['membership_id']
        group_id = self.kwargs['pk']
        try:
            return Membership.objects.filter(pk=membership_id, group__id=group_id)
        except ObjectDoesNotExist:
            return []
