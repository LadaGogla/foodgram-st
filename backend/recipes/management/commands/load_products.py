import csv
from django.core.management.base import BaseCommand
from recipes.models import Product

class Command(BaseCommand):
    help = 'Загрузка ингредиентов из data/ingredients.csv в базу данных'

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.csv'
        added = 0
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    continue
                name, unit = row
                obj, created = Product.objects.get_or_create(name=name.strip(), unit=unit.strip())
                if created:
                    added += 1
        self.stdout.write(self.style.SUCCESS(f'Загружено {added} ингредиентов.')) 