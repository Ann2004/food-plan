from django.db import models


class MealType(models.TextChoices):
    BREAKFAST = 'breakfast', 'Завтрак'
    LUNCH = 'lunch', 'Обед'
    DINNER = 'dinner', 'Ужин'
    DESSERT = 'dessert', 'Десерт'


class DietType(models.TextChoices):
    CLASSIC = 'classic', 'Классическая'
    LOW_CARB = 'low_carb', 'Низкоуглеводная'
    VEGETARIAN = 'vegetarian', 'Вегетарианская'
    KETO = 'keto', 'Кето'


class SubscriptionPeriod(models.IntegerChoices):
    MONTH_1 = 1, '1 месяц'
    MONTH_3 = 3, '3 месяца'
    MONTH_6 = 6, '6 месяцев'
    MONTH_12 = 12, '12 месяцев'


class Allergy(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название аллергена')

    class Meta:
        verbose_name = 'Аллергия'
        verbose_name_plural = 'Аллергии'

    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название ингредиента')
    calories_per_100g = models.PositiveIntegerField(default=0, verbose_name='Калорийность (ккал на 100г)')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название блюда')
    description = models.TextField(verbose_name='Описание / процесс приготовления')
    image = models.ImageField(upload_to='recipes/', blank=True, null=True, verbose_name='Изображение')
    meal_type = models.CharField(max_length=20, choices=MealType.choices, verbose_name='Тип приема пищи')
    suitable_for_diet = models.CharField(
        max_length=20, 
        choices=DietType.choices,
        default=DietType.CLASSIC,
        verbose_name='Подходит для диеты'
    )
    contains_allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name='Содержит аллергены'
    )
    cooking_time = models.PositiveSmallIntegerField(default=30, verbose_name='Время приготовления (мин)')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f"{self.name} ({self.meal_type})"
    

class RecipeIngredient(models.Model):
    """
    Модель для связи рецепта и ингредиента.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients', verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    quantity_grams = models.PositiveIntegerField(verbose_name='Количество (в граммах на 1 порцию)')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity_grams}г для '{self.recipe.name}'"