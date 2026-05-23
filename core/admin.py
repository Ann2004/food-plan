from django.contrib import admin

from .models import (
    Allergy,
    Ingredient,
    Profile,
    Recipe,
    RecipeIngredient,
    Subscription,
    Review,
    PromoCode,
)


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
