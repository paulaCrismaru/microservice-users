# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

import uuid


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
