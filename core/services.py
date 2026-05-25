import logging
import random
from datetime import date, timedelta

from .models import DailyMenu, Recipe

logger = logging.getLogger(__name__)


def generate_daily_menu(subscription, target_date):
    allergy_ids = list(subscription.allergies.values_list("pk", flat=True))
    yesterday = target_date - timedelta(days=1)

    for meal_type in subscription.meals.all():
        recipes = Recipe.objects.filter(
            meal_type=meal_type,
            suitable_for_diet=subscription.diet_type,
        )

        if allergy_ids:
            recipes = recipes.exclude(
                ingredients__ingredient__contains_allergies__pk__in=allergy_ids
            )

        recipes = recipes.distinct()

        yesterday_menu = DailyMenu.objects.filter(
            subscription=subscription,
            date=yesterday,
            meal_type=meal_type,
        ).first()

        if yesterday_menu:
            candidates = list(recipes.exclude(pk=yesterday_menu.recipe.pk))
        else:
            candidates = list(recipes)

        if not candidates:
            candidates = list(recipes)

        if not candidates:
            logger.warning(
                "No recipes for meal_type=%s, diet=%s, subscription #%s",
                meal_type.code,
                subscription.diet_type,
                subscription.id,
            )
            continue

        chosen = random.choice(candidates)

        DailyMenu.objects.update_or_create(
            subscription=subscription,
            date=target_date,
            meal_type=meal_type,
            defaults={"recipe": chosen},
        )
