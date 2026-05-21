from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from django.shortcuts import get_object_or_404

from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import Profile, Recipe


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
            # login(request, updated_user)
            update_session_auth_hash(request, updated_user)

    show_edit = request.method == "POST" and not profile_form.is_valid()

    return render(
        request,
        "lk.html",
        {
            "success_message": success_message,
            "form": profile_form,
            "show_edit": show_edit,
        },
    )


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe.objects.prefetch_related('ingredients__ingredient'), pk=pk)
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


def order(request):
    if request.method == "POST" and not request.user.is_authenticated:
        login_url = reverse("auth")
        redirect_url = add_query_params(login_url, {"next": request.path})
        return redirect(redirect_url)

    return render(request, "order.html")
