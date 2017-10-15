# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

import utils


class Membership(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()


Group.add_to_class('string_date', models.CharField(max_length=18, default=utils.get_now_string))
Group.add_to_class('admins', models.ManyToManyField(User, through=Membership))
Group._meta.get_field('name')._unique = False
