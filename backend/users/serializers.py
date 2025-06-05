from rest_framework import serializers
from .models import CustomUser, Follow
from djoser.serializers import UserCreateSerializer, TokenSerializer as DjoserTokenSerializer

class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
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
    auth_token = serializers.CharField(source='key')  # Ключевое изменение!

    class Meta(DjoserTokenSerializer.Meta):
        fields = ('auth_token',)  # Теперь возвращает {"auth_token": "токен"}

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
        return None  # Лучше возвращать None вместо пустой строки

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
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('avatar',)