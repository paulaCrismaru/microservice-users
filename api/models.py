# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
# Create your models here.

import uuid

import utils


class Friendships(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    sender = models.ForeignKey(User, related_name="request_sender")
    receiver = models.ForeignKey(User, related_name="request_receiver")
    acceptance = models.BooleanField(default=False)

    def __getitem__(self, item):
        items = {
            'sender': self.sender,
            'receiver': self.receiver,
            'acceptance': self.acceptance,
        }
        try:
            return items[item]
        except KeyError:
            raise NotImplementedError()


class Membership(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()


Group.add_to_class('string_date', models.CharField(max_length=18, default=utils.get_now_string))
Group.add_to_class('admins', models.ManyToManyField(User, through=Membership))
Group._meta.get_field('name')._unique = False
