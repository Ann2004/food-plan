from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from core import views

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", views.home, name="home"),
        path("auth/", views.auth, name="auth"),
        path("logout/", views.logout_view, name="logout"),
        path("registration/", views.registration, name="registration"),
        path("lk/", views.personal_account, name="lk"),
        path("recipe/<int:pk>/", views.recipe_detail, name="recipe_detail"),
        path("order/", views.order, name="order"),
        path(
            "subscription/<int:pk>/",
            views.subscription_detail,
            name="subscription_detail",
        ),
        path(
            "subscription/<int:pk>/today/",
            views.daily_menu,
            name="daily_menu",
        ),
        path(
            "subscription/<int:subscription_pk>/recipe/<int:daily_menu_pk>/",
            views.daily_recipe_detail,
            name="daily_recipe_detail",
        ),
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
        path('review/create/', views.create_review, name='create_review'),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
