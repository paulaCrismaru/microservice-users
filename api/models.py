# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Friendships(models.Model):
    sender = models.ForeignKey(User, related_name="request_sender")
    receiver = models.ForeignKey(User, related_name="request_receiver")
    acceptance = models.BooleanField(default=False)
