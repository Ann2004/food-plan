import calendar
from datetime import date
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import LoginForm, ProfileForm, RegistrationForm, ReviewForm, SubscriptionForm
from .models import Allergy, MealType, Profile, Recipe, Subscription, PromoCode, Review, calculate_price


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

    if request.method == "POST":
        promo_code = request.POST.get("promo_code")

        if promo_code and not request.POST.get("diet_type"):
            promo = PromoCode.objects.filter(
                code__iexact=promo_code,
            ).first()

            if not promo or not promo.is_valid:
                messages.error(request, "Промокод недействителен")

            form = SubscriptionForm()
            context = {
                "form": form,
                "allergies": allergies,
                "meal_types": meal_types,
                "price": 0,
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
                ),
                start_date=start,
                end_date=end,
                status=Subscription.Status.ACTIVE,
            )
            if selected_meals:
                subscription.meals.set(selected_meals)

            selected_allergies = request.POST.getlist("allergies")
            if selected_allergies:
                subscription.allergies.set(selected_allergies)

            return redirect("lk")
    else:
        form = SubscriptionForm()

    context = {
        "form": form,
        "allergies": allergies,
        "meal_types": meal_types,
        "price": 0,
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
