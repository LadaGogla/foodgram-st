from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Dish, Product, DishProduct
from django.db import transaction
from django.core.files import File
import os
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовых пользователей и рецепты'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            
            Dish.objects.all().delete()
            
            products = Product.objects.all()[:6]  

            avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            users_data = [
                {
                    'username': 'solomonia',
                    'email': 'solomonia@example.com',
                    'password': 'testpass123',
                    'first_name': 'Соломония',
                    'last_name': 'Вкуснова',
                    'avatar': 'ava_1.png',
                },
                {
                    'username': 'dionisiy',
                    'email': 'dionisiy@example.com',
                    'password': 'testpass123',
                    'first_name': 'Дионисий',
                    'last_name': 'Добрый',
                    'avatar': 'ava_2.png',
                },
                {
                    'username': 'sigklitikiya',
                    'email': 'sigklitikiya@example.com',
                    'password': 'testpass123',
                    'first_name': 'Сигклитикия',
                    'last_name': 'Рецептова',
                    'avatar': 'ava_3.png',
                },
            ]
            users = []
            for user_data in users_data:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'password': user_data['password'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                    }
                )
                avatar_path = os.path.join(avatars_dir, user_data['avatar'])
                if os.path.exists(avatar_path):
                    with open(avatar_path, 'rb') as avatar_file:
                        user.avatar.save(user_data['avatar'], File(avatar_file), save=True)
                users.append(user)

            dishes_data = [
                {
                    'creator': users[0],
                    'title': 'Морс',
                    'description': 'Освежающий ягодный напиток',
                    'cook_time': 15,
                },
                {
                    'creator': users[0],
                    'title': 'Глинтвейн',
                    'description': 'Традиционный зимний напиток',
                    'cook_time': 30,
                },
                {
                    'creator': users[0],
                    'title': 'Пицца',
                    'description': 'Итальянское блюдо с различными начинками',
                    'cook_time': 40,
                },
                {
                    'creator': users[1],
                    'title': 'Лазанья',
                    'description': 'Итальянское блюдо из слоев теста',
                    'cook_time': 60,
                },
                {
                    'creator': users[1],
                    'title': 'Джелато',
                    'description': 'Итальянское мороженое',
                    'cook_time': 45,
                },
                {
                    'creator': users[1],
                    'title': 'Торт',
                    'description': 'Сладкий десерт',
                    'cook_time': 120,
                },
                {
                    'creator': users[2],
                    'title': 'Холодец',
                    'description': 'Традиционное блюдо из застывшего бульона',
                    'cook_time': 240,
                },
                {
                    'creator': users[2],
                    'title': 'Салат',
                    'description': 'Легкое блюдо из свежих овощей',
                    'cook_time': 20,
                },
                {
                    'creator': users[2],
                    'title': 'Жаркое',
                    'description': 'Традиционное мясное блюдо',
                    'cook_time': 90,
                },
            ]

            media_dir = os.path.join(settings.MEDIA_ROOT, 'recipes')
            for idx, dish_data in enumerate(dishes_data, start=19):
                dish = Dish.objects.create(
                    creator=dish_data['creator'],
                    title=dish_data['title'],
                    description=dish_data['description'],
                    cook_time=dish_data['cook_time'],
                )
                for product in products[:3]:
                    DishProduct.objects.create(
                        dish=dish,
                        product=product,
                        quantity=100
                    )
                image_path = os.path.join(media_dir, f'dish_{idx}.png')
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        dish.image.save(f'dish_{idx}.png', File(img_file), save=True)

            self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы')) 