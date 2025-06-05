from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

MIN_QUANTITY = 1
MAX_QUANTITY = 32_000

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'

class Recipe(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    description = models.TextField(
        verbose_name='Описание рецепта',
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/',
        null=True,
        blank=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта',
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
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент',
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
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'

class Favourite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Рецепт',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'

class PurchaseList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchase_lists',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchase_lists',
        verbose_name='Рецепт',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в покупки'

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