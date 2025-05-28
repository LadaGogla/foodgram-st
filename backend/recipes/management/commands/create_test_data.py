from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Dish, Product, DishProduct
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовых пользователей и рецепты'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Создаем продукты
            products = [
                Product.objects.get_or_create(name='Сахар', unit='г')[0],
                Product.objects.get_or_create(name='Соль', unit='г')[0],
                Product.objects.get_or_create(name='Мука', unit='г')[0],
                Product.objects.get_or_create(name='Яйцо', unit='шт')[0],
                Product.objects.get_or_create(name='Молоко', unit='мл')[0],
                Product.objects.get_or_create(name='Масло сливочное', unit='г')[0],
            ]

            # Создаем пользователей
            users = [
                User.objects.create_user(
                    username='solomonia',
                    email='solomonia@example.com',
                    password='testpass123',
                    first_name='Соломония',
                    last_name='Вкуснова'
                ),
                User.objects.create_user(
                    username='dionisiy',
                    email='dionisiy@example.com',
                    password='testpass123',
                    first_name='Дионисий',
                    last_name='Добрый'
                ),
                User.objects.create_user(
                    username='sigklitikiya',
                    email='sigklitikiya@example.com',
                    password='testpass123',
                    first_name='Сигклитикия',
                    last_name='Рецептова'
                ),
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

            for dish_data in dishes_data:
                dish = Dish.objects.create(
                    creator=dish_data['creator'],
                    title=dish_data['title'],
                    description=dish_data['description'],
                    cook_time=dish_data['cook_time'],
                )
                # Добавляем продукты
                for product in products[:3]:  # Берем первые 3 продукта для каждого блюда
                    DishProduct.objects.create(
                        dish=dish,
                        product=product,
                        quantity=100
                    )

            self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы')) 