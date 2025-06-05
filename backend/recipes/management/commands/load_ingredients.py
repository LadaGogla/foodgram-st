from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import json
import os

class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON файла'

    def handle(self, *args, **kwargs):
        
        file_path = os.path.join('data', 'ingredients.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ingredients = json.load(file)
                
                for ingredient in ingredients:
                    Ingredient.objects.get_or_create(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Успешно загружено {len(ingredients)} ингредиентов')
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Ошибка при чтении JSON файла')
            ) 