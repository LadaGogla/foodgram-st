from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return f'{self.username} ({self.first_name} {self.last_name})'

class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='following',
        on_delete=models.CASCADE,
    )
    leader = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='followers',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['follower', 'leader'], name='unique_follow')
        ]

    def __str__(self):
        return f'{self.follower} подписан на {self.leader}' 