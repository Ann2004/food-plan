from datetime import date

from django.contrib import admin

from .models import (
    Allergy,
    DailyMenu,
    Ingredient,
    MealType,
    Profile,
    Recipe,
    RecipeIngredient,
    Subscription,
    SubscriptionPeriod,
    Review,
    PromoCode,
)
from .services import generate_daily_menu


@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "base_price")


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "calories_per_100g")
    search_fields = ("name",)
    filter_horizontal = ("contains_allergies",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user")


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ["ingredient"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "meal_type", "suitable_for_diet", "cooking_time")
    list_filter = ("meal_type", "suitable_for_diet")
    search_fields = ("name", "description")
    inlines = [RecipeIngredientInline]
    fieldsets = (
        (None, {"fields": ("name", "description", "image", "cooking_time")}),
        ("Типы", {"fields": ("meal_type", "suitable_for_diet")}),
    )


@admin.register(SubscriptionPeriod)
class SubscriptionPeriodAdmin(admin.ModelAdmin):
    list_display = ("months", "name", "price_multiplier")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "diet_type",
        "period",
        "persons_count",
        "price",
        "start_date",
        "end_date",
        "status",
    )
    list_filter = ("diet_type", "status", "period")
    search_fields = ("user__username", "user__email")
    filter_horizontal = ("meals", "allergies")
    actions = ["refresh_daily_menu"]
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Параметры питания",
            {
                "fields": (
                    "diet_type",
                    "persons_count",
                    "meals",
                    "allergies",
                    "calories_per_day",
                )
            },
        ),
        ("Оплата", {"fields": ("price", "payment_id")}),
        ("Период", {"fields": ("period", "start_date", "end_date")}),
    )

    @admin.action(description="Пересоздать меню на сегодня")
    def refresh_daily_menu(self, request, queryset):
        today = date.today()
        for subscription in queryset:
            DailyMenu.objects.filter(
                subscription=subscription,
                date=today,
            ).delete()
            generate_daily_menu(subscription, today)
        self.message_user(request, f"Меню пересоздано для {queryset.count()} подписок.")


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "subscription", "date", "meal_type", "recipe")
    list_filter = ("date", "meal_type")
    search_fields = ("subscription__user__username", "subscription__user__email")
    readonly_fields = ("subscription", "date", "meal_type", "recipe")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "rating", "created_at"]
    list_filter = [
        "rating",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_percent",
        "active",
        "valid_from",
        "valid_to",
    )

    list_filter = ("active",)
    search_fields = ("code",)
