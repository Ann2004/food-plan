from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import LoginForm, ProfileForm, RegistrationForm, ReviewForm
from .models import Profile, Recipe, Subscription, PromoCode


def home(request):
    return render(request, "index.html")


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
        request.user.subscriptions.all().filter(status="active").order_by("-start_date")
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
        Recipe.objects.prefetch_related("ingredients__ingredient"),
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
        Subscription.objects.prefetch_related("allergies"),
        pk=pk,
        user=request.user,
    )

    if (
        subscription.status == "active"
        and subscription.end_date < timezone.now().date()
    ):
        subscription.status = "expired"
        subscription.save()

    recipes = Recipe.objects.filter(suitable_for_diet=subscription.diet_type)

    breakfast_recipes = None
    lunch_recipes = None
    dinner_recipes = None
    dessert_recipes = None

    meals_count = subscription.meals_count

    if meals_count >= 1:
        breakfast_recipes = recipes.filter(meal_type="breakfast")

    if meals_count >= 2:
        lunch_recipes = recipes.filter(meal_type="lunch")

    if meals_count >= 3:
        dinner_recipes = recipes.filter(meal_type="dinner")

    if meals_count >= 4:
        dessert_recipes = recipes.filter(meal_type="dessert")

    context = {
        "subscription": subscription,
        "breakfast_recipes": breakfast_recipes,
        "lunch_recipes": lunch_recipes,
        "dinner_recipes": dinner_recipes,
        "dessert_recipes": dessert_recipes,
    }

    return render(request, "subscription.html", context)


def order(request):

    if request.method == "POST":
        promo_code = request.POST.get("promo_code")

        if promo_code:
            promo = PromoCode.objects.filter(
                code__iexact=promo_code,
            ).first()

            if not promo or not promo.is_valid:
                messages.error(request, "Промокод недействителен")

        elif not request.user.is_authenticated:
            login_url = reverse("auth")
            redirect_url = add_query_params(login_url, {"next": request.path})
            return redirect(redirect_url)

    return render(request, "order.html")


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
