import calendar
import json
import logging
import uuid
from datetime import date
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from decimal import Decimal

from yookassa import Configuration, Payment

from .forms import LoginForm, ProfileForm, RegistrationForm, ReviewForm, SubscriptionForm
from .models import Allergy, DailyMenu, MealType, Profile, Recipe, Subscription, SubscriptionPeriod, PromoCode, Review, calculate_price
from .services import generate_daily_menu

logger = logging.getLogger(__name__)

Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)


def home(request):
    reviews = Review.objects.filter(is_moderated=True).select_related("user").order_by("-created_at")
    
    context = {
        "reviews": reviews,
    }
    return render(request, "index.html", context)


def auth(request):
    login_form = LoginForm(request.POST or None)

    if request.method == "POST" and login_form.is_valid():
        login(request, login_form.get_user())
        return redirect("home")

    return render(request, "auth.html", {"form": login_form})


def registration(request):
    next_url = request.GET.get("next") or request.POST.get("next") or ""
    registration_form = RegistrationForm(request.POST or None)

    if request.method == "POST" and registration_form.is_valid():
        new_user = registration_form.save()
        login(request, new_user)
        return redirect(next_url or "home")

    return render(
        request,
        "registration.html",
        {"form": registration_form, "next_url": next_url},
    )


def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("home")


def add_query_params(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


@login_required
def personal_account(request):

    Profile.objects.get_or_create(user=request.user)

    expired_subscriptions = request.user.subscriptions.filter(
        end_date__lt=timezone.now().date(), status="active"
    )

    expired_subscriptions.update(status="expired")

    success_message = ""

    profile_form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
        initial={
            "first_name": request.user.first_name,
            "email": request.user.email,
        },
    )

    if request.method == "POST" and profile_form.is_valid():
        updated_user = profile_form.save()

        success_message = "Данные сохранены."

        if profile_form.cleaned_data.get("new_password"):
            update_session_auth_hash(request, updated_user)

    show_edit = request.method == "POST" and not profile_form.is_valid()

    subscriptions = (
        request.user.subscriptions.filter(
            status__in=["active", "new", "paid"]
        ).order_by("-start_date")
    )

    return render(
        request,
        "lk.html",
        {
            "success_message": success_message,
            "form": profile_form,
            "show_edit": show_edit,
            "subscriptions": subscriptions,
        },
    )


@staff_member_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related("ingredients__ingredient__contains_allergies"),
        pk=pk,
    )

    recipe_ingredients = recipe.ingredients.all()

    total_calories = sum(
        ri.ingredient.calories_per_100g * ri.quantity_grams / 100
        for ri in recipe_ingredients
    )

    context = {
        "recipe": recipe,
        "recipe_ingredients": recipe_ingredients,
        "total_calories": int(total_calories),
    }

    return render(request, "card.html", context)


@login_required
def daily_menu(request, pk):
    subscription = get_object_or_404(
        Subscription,
        pk=pk,
        user=request.user,
        status=Subscription.Status.ACTIVE,
    )

    generate_daily_menu(subscription, date.today())

    menus = DailyMenu.objects.filter(
        subscription=subscription,
        date=date.today(),
    ).select_related("meal_type", "recipe").order_by("meal_type")

    menu_data = []
    for menu in menus:
        recipe = menu.recipe
        recipe_ingredients = recipe.ingredients.select_related("ingredient").all()
        scaled_ingredients = [
            {
                "name": ri.ingredient.name,
                "quantity": ri.quantity_grams * subscription.persons_count,
            }
            for ri in recipe_ingredients
        ]
        total_calories = sum(
            ri.ingredient.calories_per_100g * ri.quantity_grams / 100
            for ri in recipe_ingredients
        )
        menu_data.append({
            "menu": menu,
            "recipe": recipe,
            "scaled_ingredients": scaled_ingredients,
            "total_calories": int(total_calories),
        })

    context = {
        "subscription": subscription,
        "menu_data": menu_data,
    }
    return render(request, "daily_menu.html", context)


@login_required
def daily_recipe_detail(request, subscription_pk, daily_menu_pk):
    subscription = get_object_or_404(
        Subscription,
        pk=subscription_pk,
        user=request.user,
        status=Subscription.Status.ACTIVE,
    )

    daily_menu = get_object_or_404(
        DailyMenu,
        pk=daily_menu_pk,
        subscription=subscription,
    )

    recipe = daily_menu.recipe
    recipe_ingredients = recipe.ingredients.select_related("ingredient").all()

    scaled_ingredients = [
        {
            "name": ri.ingredient.name,
            "quantity": ri.quantity_grams * subscription.persons_count,
        }
        for ri in recipe_ingredients
    ]

    total_calories = sum(
        ri.ingredient.calories_per_100g * ri.quantity_grams / 100
        for ri in recipe_ingredients
    )

    context = {
        "subscription": subscription,
        "daily_menu": daily_menu,
        "recipe": recipe,
        "scaled_ingredients": scaled_ingredients,
        "total_calories": int(total_calories),
        "persons_count": subscription.persons_count,
    }
    return render(request, "daily_recipe_card.html", context)


@login_required
def subscription_detail(request, pk):

    subscription = get_object_or_404(
        Subscription.objects.prefetch_related("meals"),
        pk=pk,
        user=request.user,
    )

    if (
        subscription.status == "active"
        and subscription.end_date
        and subscription.end_date < timezone.now().date()
    ):
        subscription.status = "expired"
        subscription.save()

    recipes = Recipe.objects.filter(suitable_for_diet=subscription.diet_type)

    meal_recipes_list = [
        (meal, recipes.filter(meal_type=meal))
        for meal in subscription.meals.all()
    ]

    context = {
        "subscription": subscription,
        "meal_recipes_list": meal_recipes_list,
    }

    return render(request, "subscription.html", context)


def order(request):
    allergies = Allergy.objects.all()
    meal_types = MealType.objects.all()

    meal_prices = json.dumps({str(mt.pk): mt.base_price for mt in meal_types})
    period_multipliers = json.dumps({
        str(sp.months): float(sp.price_multiplier)
        for sp in SubscriptionPeriod.objects.all()
    })

    if request.method == "POST":
        promo_code_str = request.POST.get("promo_code", "").strip()
        promo = None
        if promo_code_str:
            promo = PromoCode.objects.filter(
                code__iexact=promo_code_str,
            ).first()
            if not promo or not promo.is_valid:
                messages.error(request, "Промокод недействителен")
                promo = None

        if "apply_promo" in request.POST:
            form = SubscriptionForm()
            selected_meals = [
                pk for pk in request.POST.getlist("meals") if pk
            ]
            period_id = request.POST.get("period")
            period = SubscriptionPeriod.objects.filter(months=period_id).first()
            persons_count = int(request.POST.get("persons_count", 1))
            original_price = 0
            price = 0
            if period and selected_meals:
                original_price = calculate_price(
                    persons_count, period, selected_meals
                )
                price = calculate_price(
                    persons_count, period, selected_meals, promo_code=promo
                )
            context = {
                "form": form,
                "allergies": allergies,
                "meal_types": meal_types,
                "price": price,
                "original_price": original_price,
                "promo": promo,
                "promo_discount": promo.discount_percent if promo else 0,
                "selected_meals": selected_meals,
                "meal_prices": meal_prices,
                "period_multipliers": period_multipliers,
            }
            return render(request, "order.html", context)

        if not request.user.is_authenticated:
            login_url = reverse("auth")
            redirect_url = add_query_params(login_url, {"next": request.path})
            return redirect(redirect_url)

        form = SubscriptionForm(request.POST)
        if form.is_valid():
            selected_meals = [
                pk for pk in request.POST.getlist("meals") if pk
            ]

            period = form.cleaned_data["period"]
            start = timezone.now().date()
            month = start.month - 1 + period.months
            year = start.year + month // 12
            month = month % 12 + 1
            day = min(start.day, calendar.monthrange(year, month)[1])
            end = date(year, month, day)

            calories = int(request.POST.get("calories_per_day", 2000))
            if calories < 100:
                calories = 100
            elif calories > 5000:
                calories = 5000

            subscription = Subscription.objects.create(
                user=request.user,
                diet_type=form.cleaned_data["diet_type"],
                period=period,
                persons_count=int(form.cleaned_data["persons_count"]),
                calories_per_day=calories,
                price=calculate_price(
                    int(form.cleaned_data["persons_count"]),
                    period,
                    selected_meals,
                    promo_code=promo,
                ),
                start_date=start,
                end_date=end,
                status=Subscription.Status.NEW,
            )
            if selected_meals:
                subscription.meals.set(selected_meals)

            selected_allergies = request.POST.getlist("allergies")
            if selected_allergies:
                subscription.allergies.set(selected_allergies)

            request.session["current_subscription_id"] = subscription.id
            return redirect("payment-create")
    else:
        form = SubscriptionForm()

    context = {
        "form": form,
        "allergies": allergies,
        "meal_types": meal_types,
        "price": 0,
        "promo": None,
        "promo_discount": 0,
        "meal_prices": meal_prices,
        "period_multipliers": period_multipliers,
    }

    return render(request, "order.html", context)


@login_required
def create_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Спасибо за ваш отзыв!")
            return redirect("lk")
    else:
        form = ReviewForm()

    return render(request, "review.html", {"form": form})


@login_required
def payment_create(request):
    subscription_id = request.session.get("current_subscription_id")
    if not subscription_id:
        return redirect("order")

    subscription = get_object_or_404(
        Subscription,
        pk=subscription_id,
        user=request.user,
        status=Subscription.Status.NEW,
    )

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {
                "value": str(subscription.price),
                "currency": "RUB",
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(reverse("payment-success")),
            },
            "description": f"Подписка #{subscription.id}",
            "metadata": {
                "subscription_id": subscription.id,
            },
        },
        idempotence_key,
    )

    subscription.payment_id = payment.id
    subscription.save()

    return redirect(payment.confirmation.confirmation_url)


@login_required
def payment_success(request):
    subscription_id = request.session.get("current_subscription_id")
    subscription = None

    if subscription_id:
        subscription = Subscription.objects.filter(
            pk=subscription_id,
            user=request.user,
        ).first()
        if subscription and subscription.status == Subscription.Status.PAID:
            if "current_subscription_id" in request.session:
                del request.session["current_subscription_id"]

    return render(
        request,
        "payment-success.html",
        {"subscription": subscription},
    )


def payment_failure(request):
    return render(request, "payment-failure.html")


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    try:
        event = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return HttpResponse(status=400)

    payment_id = event.get("object", {}).get("id")
    status = event.get("object", {}).get("status")

    if not payment_id or not status:
        return HttpResponse(status=400)

    subscription = Subscription.objects.filter(payment_id=payment_id).first()
    if not subscription:
        logger.warning("Webhook: subscription not found for payment_id=%s", payment_id)
        return HttpResponse(status=404)

    if status == "succeeded":
        subscription.status = Subscription.Status.ACTIVE
        if not subscription.start_date:
            subscription.start_date = timezone.now().date()
        subscription.save()
        logger.info(
            "Subscription #%s activated via payment %s",
            subscription.id,
            payment_id,
        )
    elif status == "canceled":
        subscription.status = Subscription.Status.CANCELLED
        subscription.save()
        logger.info(
            "Subscription #%s cancelled via payment %s",
            subscription.id,
            payment_id,
        )

    return HttpResponse(status=200)
