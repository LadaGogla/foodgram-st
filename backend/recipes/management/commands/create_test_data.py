from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Dish, Product, DishProduct
from django.db import transaction
from django.core.files import File
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовых пользователей и рецепты'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Удаляем старые блюда
            Dish.objects.all().delete()
            # Создаем продукты
            products = [
                Product.objects.get_or_create(name='Сахар', unit='г')[0],
                Product.objects.get_or_create(name='Соль', unit='г')[0],
                Product.objects.get_or_create(name='Мука', unit='г')[0],
                Product.objects.get_or_create(name='Яйцо', unit='шт')[0],
                Product.objects.get_or_create(name='Молоко', unit='мл')[0],
                Product.objects.get_or_create(name='Масло сливочное', unit='г')[0],
            ]

            # Получаем или создаём пользователей
            users = [
                User.objects.get_or_create(
                    username='solomonia',
                    defaults={
                        'email': 'solomonia@example.com',
                        'password': 'testpass123',
                        'first_name': 'Соломония',
                        'last_name': 'Вкуснова'
                    }
                )[0],
                User.objects.get_or_create(
                    username='dionisiy',
                    defaults={
                        'email': 'dionisiy@example.com',
                        'password': 'testpass123',
                        'first_name': 'Дионисий',
                        'last_name': 'Добрый'
                    }
                )[0],
                User.objects.get_or_create(
                    username='sigklitikiya',
                    defaults={
                        'email': 'sigklitikiya@example.com',
                        'password': 'testpass123',
                        'first_name': 'Сигклитикия',
                        'last_name': 'Рецептова'
                    }
                )[0],
            ]

            # Создаем рецепты
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

            media_dir = os.path.join('media', 'recipes')
            for idx, dish_data in enumerate(dishes_data, start=19):
                dish = Dish.objects.create(
                    creator=dish_data['creator'],
                    title=dish_data['title'],
                    description=dish_data['description'],
                    cook_time=dish_data['cook_time'],
                )
                # Добавляем продукты
                for product in products[:3]:
                    DishProduct.objects.create(
                        dish=dish,
                        product=product,
                        quantity=100
                    )
                # Присваиваем изображение, если файл существует
                image_path = os.path.join(media_dir, f'dish_{idx}.png')
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        dish.image.save(f'dish_{idx}.png', File(img_file), save=True)

            self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы')) 