from rest_framework import serializers
from .models import CustomUser, Follow
from djoser.serializers import UserCreateSerializer, TokenSerializer as DjoserTokenSerializer
from rest_framework.response import Response
import base64
from django.core.files.base import ContentFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        return representation

class CustomTokenSerializer(DjoserTokenSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta(DjoserTokenSerializer.Meta):
        fields = ('auth_token',) 

class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')
        read_only_fields = ('id', 'email', 'username', 'last_login', 'is_superuser', 
                          'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions')

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None  

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, leader=obj).exists()
        return False

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField(read_only=True)
    leader = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'leader')
        read_only_fields = ('id', 'follower', 'leader')

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class AvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(write_only=True, required=True, allow_null=False)

    class Meta:
        model = CustomUser
        fields = ('avatar',)

    def update(self, instance, validated_data):
        logger.info(f"AvatarSerializer update called for user {instance.pk}")
        avatar_data = validated_data.get('avatar')
        logger.info(f"Received avatar_data: {avatar_data[:50]}..." if isinstance(avatar_data, str) and len(avatar_data) > 50 else f"Received avatar_data: {avatar_data}")

        if avatar_data is not None:
            if avatar_data == 'null':
                 logger.info("Avatar data is 'null', attempting to delete avatar.")
                 if instance.avatar:
                     try:
                         instance.avatar.delete(save=True)
                         instance.avatar = None
                         instance.save()
                         logger.info("Avatar deleted successfully.")
                     except Exception as e:
                         logger.error(f"Error deleting avatar: {e}", exc_info=True)
                         raise serializers.ValidationError(f"Ошибка при удалении аватара: {e}")
                 else:
                     logger.info("No avatar to delete.")
            elif isinstance(avatar_data, str) and avatar_data.startswith('data:image'):
                logger.info("Avatar data is base64 string, attempting to save.")
                if instance.avatar:
                    
                    try:
                         instance.avatar.delete(save=False)
                         logger.info("Old avatar deleted before saving new one.")
                    except Exception as e:
                         logger.warning(f"Could not delete old avatar: {e}")

                try:
                    format, imgstr = avatar_data.split(';base64,')
                    ext = format.split('/')[-1]
                    if ext.lower() not in ['png', 'jpg', 'jpeg']:
                         logger.warning(f"Unsupported image format: {ext}")
                         raise serializers.ValidationError("Неподдерживаемый формат изображения.")
                    file_name = f"avatar_{instance.pk}.{ext.lower()}"
                    instance.avatar.save(file_name, ContentFile(base64.b64decode(imgstr)), save=True)
                    logger.info(f"New avatar saved successfully: {file_name}")
                except Exception as e:
                    logger.error(f"Error processing base64 or saving file: {e}", exc_info=True)
                    raise serializers.ValidationError(f"Ошибка при обработке base64 или сохранении файла: {e}")
            else:
                 logger.warning(f"Incorrect data format for avatar: {type(avatar_data)}")
                 raise serializers.ValidationError("Некорректный формат данных для аватара.")

        return instance