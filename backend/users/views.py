from rest_framework import viewsets, permissions, filters, status
from .models import CustomUser, Follow
from .serializers import CustomUserSerializer, FollowSerializer, ChangePasswordSerializer, AvatarSerializer, CustomUserCreateSerializer, UserSerializerWithRecipes
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['retrieve', 'list', 'subscribe', 'unsubscribe', 'subscriptions']:
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'subscriptions':
            return UserSerializerWithRecipes
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        # Проверка на существующего пользователя
        email = request.data.get('email')
        username = request.data.get('username')
        
        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {'email': 'Пользователь с таким email уже существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if CustomUser.objects.filter(username=username).exists():
            return Response(
                {'username': 'Пользователь с таким username уже существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='set_password')
    def set_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {'current_password': 'Неверный текущий пароль.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_avatar(self, request):
        serializer = AvatarSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def set_avatar_me(self, request):
        serializer = AvatarSerializer(instance=request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_serializer = CustomUserSerializer(request.user, context={'request': request})
            avatar_url = user_serializer.data.get('avatar')
            return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def delete_avatar_me(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        leader = get_object_or_404(CustomUser, pk=pk)
        user = request.user

        if user == leader:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            try:
                Follow.objects.create(follower=user, leader=leader)
                serializer = UserSerializerWithRecipes(leader, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            follow_instance = Follow.objects.filter(follower=user, leader=leader)
            if follow_instance.exists():
                follow_instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        followed_users = CustomUser.objects.filter(leader__follower=user)

        page = self.paginate_queryset(followed_users)
        if page is not None:
            serializer = UserSerializerWithRecipes(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializerWithRecipes(followed_users, many=True, context={'request': request})
        return Response(serializer.data)

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(follower=self.request.user)

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)