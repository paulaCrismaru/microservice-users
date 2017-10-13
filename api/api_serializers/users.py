from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from rest_framework import serializers

from api import utils


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email','user_id')

    @staticmethod
    def get_user_id(obj):
        return utils.encode(obj.id)


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        if validated_data.get('email'):
            try:
                User.objects.get(email=validated_data['email'])
            except ObjectDoesNotExist:
                pass
            else:
                raise ValidationError("A user with that email already exists.")
        return User.objects.create_user(**validated_data)