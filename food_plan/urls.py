from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
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
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
