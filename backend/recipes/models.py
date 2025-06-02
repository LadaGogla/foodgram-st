from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

MIN_QUANTITY = 1
MAX_QUANTITY = 32_000

class Product(models.Model):
    name = models.CharField(
        verbose_name='Название продукта',
        max_length=200,
    )
    unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.unit})'

class Dish(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name='Автор рецепта',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название блюда',
    )
    description = models.TextField(
        verbose_name='Описание блюда',
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipes/',
        null=True,
        blank=True,
    )
    products = models.ManyToManyField(
        Product,
        through='DishProduct',
        related_name='dishes',
        verbose_name='Продукты блюда',
    )
    cook_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_QUANTITY,
                message=f'Минимальное время приготовления — {MIN_QUANTITY} минута'
            ),
            MaxValueValidator(
                MAX_QUANTITY,
                message=f'Максимальное время приготовления — {MAX_QUANTITY} минут'
            )
        ],
        verbose_name='Время приготовления (мин)',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class DishProduct(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        verbose_name='Блюдо',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Продукт',
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_QUANTITY,
                message=f'Минимальное количество — {MIN_QUANTITY}'
            ),
            MaxValueValidator(
                MAX_QUANTITY,
                message=f'Максимальное количество — {MAX_QUANTITY}'
            )
        ],
        verbose_name='Количество',
    )

    class Meta:
        unique_together = ('dish', 'product')
        verbose_name = 'Продукт в блюде'
        verbose_name_plural = 'Продукты в блюде'

    def __str__(self):
        return f'{self.product} для {self.dish}'

class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Пользователь',
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Блюдо',
    )

    class Meta:
        unique_together = ('user', 'dish')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.dish} в избранное'

class PurchaseList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchase_lists',
        verbose_name='Пользователь',
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='purchase_lists',
        verbose_name='Блюдо',
    )

    class Meta:
        unique_together = ('user', 'dish')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.dish} в покупки'

class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}' 