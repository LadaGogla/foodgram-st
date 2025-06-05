from rest_framework import viewsets, permissions, filters, status
from .models import CustomUser, Follow
from .serializers import CustomUserSerializer, FollowSerializer, ChangePasswordSerializer, AvatarSerializer, CustomUserCreateSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'list']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
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

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(follower=self.request.user)

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)