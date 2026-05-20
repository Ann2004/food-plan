from django.shortcuts import render


def home(request):
    return render(request, "index.html")


def auth(request):
    return render(request, "auth.html")


def registration(request):
    return render(request, "registration.html")


def personal_account(request):
    return render(request, "lk.html")


def recipe_detail_1(request):
    return render(request, "card1.html")


def recipe_detail_2(request):
    return render(request, "card2.html")


def recipe_detail_3(request):
    return render(request, "card3.html")


def order(request):
    return render(request, "order.html")
