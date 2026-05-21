from django.contrib import admin

from .models import Allergy, Ingredient, Recipe, RecipeIngredient, Subscription, Review


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "calories_per_100g")
    search_fields = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ["ingredient"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "meal_type", "suitable_for_diet", "cooking_time")
    list_filter = ("meal_type", "suitable_for_diet", "contains_allergies")
    search_fields = ("name", "description")
    filter_horizontal = ("contains_allergies",)
    inlines = [RecipeIngredientInline]
    fieldsets = (
        (None, {"fields": ("name", "description", "image", "cooking_time")}),
        ("Типы", {"fields": ("meal_type", "suitable_for_diet")}),
        (
            "Аллергены",
            {
                "fields": ("contains_allergies",),
                "description": "Выберите все аллергены, которые содержит блюдо",
            },
        ),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "diet_type",
        "period",
        "persons_count",
        "calories_per_day",
        "meals_count",
        "start_date",
        "end_date",
        "status",
    )
    list_filter = ("diet_type", "status", "period")
    search_fields = ("user__username", "user__email")
    filter_horizontal = ("allergies",)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Параметры питания",
            {
                "fields": (
                    "diet_type",
                    "persons_count",
                    "calories_per_day",
                    "meals_count",
                    "allergies",
                )
            },
        ),
        ("Период", {"fields": ("period", "end_date")}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'created_at']
    list_filter = ['rating',]
    readonly_fields = ['created_at', 'updated_at']