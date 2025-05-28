from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Dish, Product, DishProduct
from django.core.files.base import ContentFile
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Создаёт тестовых пользователей и по одному рецепту для каждого.'

    def handle(self, *args, **kwargs):
        # Создаём пользователей
        users = [
            {'username': 'admin', 'email': 'admin@example.com', 'password': 'adminpass', 'is_superuser': True, 'is_staff': True},
            {'username': 'user1', 'email': 'user1@example.com', 'password': 'user1pass', 'is_superuser': False, 'is_staff': False},
            {'username': 'user2', 'email': 'user2@example.com', 'password': 'user2pass', 'is_superuser': False, 'is_staff': False},
        ]
        created_users = []
        for u in users:
            user, created = User.objects.get_or_create(username=u['username'], email=u['email'])
            if created:
                user.set_password(u['password'])
                user.is_superuser = u['is_superuser']
                user.is_staff = u['is_staff']
                user.save()
            created_users.append(user)
        self.stdout.write(self.style.SUCCESS(f'Создано пользователей: {len(created_users)}'))

        # Берём 3 случайных продукта
        products = list(Product.objects.all()[:3])
        if not products:
            self.stdout.write(self.style.ERROR('Нет продуктов в базе. Сначала загрузите ингредиенты!'))
            return

        # Для каждого пользователя создаём по одному рецепту
        for idx, user in enumerate(created_users):
            dish = Dish.objects.create(
                creator=user,
                title=f'Тестовое блюдо {idx+1}',
                description='Описание тестового блюда',
                cook_time=random.randint(5, 60),
                image=ContentFile(b'fake image data', name=f'test{idx+1}.jpg'),
            )
            for prod in products:
                DishProduct.objects.create(dish=dish, product=prod, quantity=random.randint(1, 5))
        self.stdout.write(self.style.SUCCESS('Тестовые рецепты созданы.')) 