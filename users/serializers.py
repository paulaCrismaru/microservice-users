from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'id')


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
                raise serializers.ValidationError({"email": ["A user with that email already exists."]})
        return User.objects.create_user(**validated_data)


class MeSerializer(UserSerializer):

    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'id')

    @staticmethod
    def get_email(obj):
        return obj.email

    @staticmethod
    def get_username(obj):
        return obj.username