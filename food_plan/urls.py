from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from core import views

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", views.home, name="home"),
        path("auth/", views.auth, name="auth"),
        path("logout/", views.logout_view, name="logout"),
        path("registration/", views.registration, name="registration"),
        path("lk/", views.personal_account, name="lk"),
        path("recipe/1/", views.recipe_detail_1, name="recipe_1"),
        path("recipe/2/", views.recipe_detail_2, name="recipe_2"),
        path("recipe/3/", views.recipe_detail_3, name="recipe_3"),
        path("order/", views.order, name="order"),
        path(
            "password-reset/",
            auth_views.PasswordResetView.as_view(
                template_name="password_reset.html",
            ),
            name="password_reset",
        ),
        path(
            "password-reset/done/",
            auth_views.PasswordResetDoneView.as_view(
                template_name="password_reset_done.html",
            ),
            name="password_reset_done",
        ),
        path(
            "reset/<uidb64>/<token>/",
            auth_views.PasswordResetConfirmView.as_view(
                template_name="password_reset_confirm.html",
            ),
            name="password_reset_confirm",
        ),
        path(
            "reset/done/",
            auth_views.PasswordResetCompleteView.as_view(
                template_name="password_reset_complete.html",
            ),
            name="password_reset_complete",
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
