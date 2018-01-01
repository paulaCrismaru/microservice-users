# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import Group, User


class Membership(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="person_name")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_name")
    admin = models.BooleanField(default=False)

    class Meta:
        unique_together = (("person", "group"),)

Group._meta.get_field('name')._unique = False
