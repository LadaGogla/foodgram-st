from rest_framework import serializers
from .models import CustomUser, Follow
from djoser.serializers import UserCreateSerializer, TokenSerializer as DjoserTokenSerializer

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')

class CustomTokenSerializer(DjoserTokenSerializer):
    class Meta:
        model = DjoserTokenSerializer.Meta.model
        fields = ('auth_token',)

class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar')
        read_only_fields = ('last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions')

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField(read_only=True)
    leader = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'leader')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('avatar',) 