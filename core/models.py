from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MealType(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Код")
    name = models.CharField(max_length=100, verbose_name="Название")
    base_price = models.PositiveIntegerField(default=0, verbose_name="Базовая цена")

    class Meta:
        verbose_name = "Тип приёма пищи"
        verbose_name_plural = "Типы приёмов пищи"

    def __str__(self):
        return self.name


class DietType(models.TextChoices):
    CLASSIC = "classic", "Классическая"
    LOW_CARB = "low_carb", "Низкоуглеводная"
    VEGETARIAN = "vegetarian", "Вегетарианская"
    KETO = "keto", "Кето"


class SubscriptionPeriod(models.Model):
    months = models.PositiveSmallIntegerField(unique=True, verbose_name="Месяцев")
    name = models.CharField(max_length=50, verbose_name="Название")
    price_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name="Множитель цены",
    )

    class Meta:
        verbose_name = "Период подписки"
        verbose_name_plural = "Периоды подписки"

    def __str__(self):
        return self.name


class Allergy(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название аллергена"
    )

    class Meta:
        verbose_name = "Аллергия"
        verbose_name_plural = "Аллергии"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name="Название ингредиента"
    )
    calories_per_100g = models.PositiveIntegerField(
        default=0, verbose_name="Калорийность (ккал на 100г)"
    )
    contains_allergies = models.ManyToManyField(
        Allergy, blank=True, verbose_name="Содержит аллергены"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание / процесс приготовления")
    image = models.ImageField(
        upload_to="recipes/", blank=True, null=True, verbose_name="Изображение"
    )
    meal_type = models.ForeignKey(
        MealType,
        on_delete=models.PROTECT,
        related_name="recipes",
        verbose_name="Тип приема пищи",
    )
    suitable_for_diet = models.CharField(
        max_length=20,
        choices=DietType.choices,
        default=DietType.CLASSIC,
        verbose_name="Подходит для диеты",
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=30, verbose_name="Время приготовления (мин)"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name} ({self.meal_type.name})"

    @property
    def allergies(self):
        seen = set()
        result = []
        for ri in self.ingredients.all():
            for allergy in ri.ingredient.contains_allergies.all():
                if allergy.pk not in seen:
                    seen.add(allergy.pk)
                    result.append(allergy)
        return result


class RecipeIngredient(models.Model):
    """
    Модель для связи рецепта и ингредиента.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    quantity_grams = models.PositiveIntegerField(
        verbose_name="Количество (в граммах на 1 порцию)"
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        unique_together = ("recipe", "ingredient")

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.quantity_grams}г для '{self.recipe.name}'"
        )


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.email


class Subscription(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        PAID = "paid", "Оплачена"
        CANCELLED = "cancelled", "Отменена"
        ACTIVE = "active", "Активна"
        EXPIRED = "expired", "Истекла"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    diet_type = models.CharField(
        max_length=20,
        choices=DietType.choices,
        verbose_name="Тип питания",
    )
    period = models.ForeignKey(
        SubscriptionPeriod,
        on_delete=models.PROTECT,
        verbose_name="Период подписки",
    )
    persons_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Количество персон",
    )
    meals = models.ManyToManyField(
        MealType,
        blank=True,
        verbose_name="Приёмы пищи",
    )
    allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        verbose_name="Аллергии",
    )
    calories_per_day = models.PositiveIntegerField(
        default=2000,
        verbose_name="Калорий в день",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Цена",
    )
    payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID платежа",
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата начала",
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата окончания",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.username} — {self.get_diet_type_display()}"


class DailyMenu(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="daily_menus",
        verbose_name="Подписка",
    )
    date = models.DateField(verbose_name="Дата")
    meal_type = models.ForeignKey(
        MealType,
        on_delete=models.PROTECT,
        verbose_name="Тип приёма пищи",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.PROTECT,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Меню дня"
        verbose_name_plural = "Меню дня"
        unique_together = ("subscription", "date", "meal_type")
        ordering = ["date", "meal_type"]

    def __str__(self):
        return f"{self.subscription} — {self.date} — {self.meal_type.name}"


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Оценка"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    image = models.ImageField(
        upload_to="reviews/", blank=True, null=True, verbose_name="Фото"
    )
    is_moderated = models.BooleanField(default=False, verbose_name="Прошел модерацию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.user.username} - {self.rating}★"


def calculate_price(persons_count, period, meal_type_ids, promo_code=None):
    meals_total = (
        MealType.objects.filter(pk__in=meal_type_ids).aggregate(
            total=models.Sum("base_price")
        )["total"]
        or 0
    )
    price = meals_total * period.price_multiplier * persons_count
    if promo_code and promo_code.is_valid:
        price = price * (Decimal("1") - Decimal(promo_code.discount_percent) / Decimal("100"))
    return price


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    discount_percent = models.PositiveSmallIntegerField(verbose_name="Скидка (%)")
    active = models.BooleanField(default=True, verbose_name="Активен")
    valid_from = models.DateTimeField(verbose_name="Действует с")
    valid_to = models.DateTimeField(verbose_name="Действует до")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    @property
    def is_valid(self):
        now = timezone.now()

        return self.active and self.valid_from <= now <= self.valid_to
