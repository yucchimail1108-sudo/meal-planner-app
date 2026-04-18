from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.shortcuts import render

def portfolio_view(request):
    return render(request, "portfolio.html")

urlpatterns = [
    path("", portfolio_view, name="top"),
    path("app/", views.home_view, name="app_home"),
    path("recipes/", include("apps.recipes.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("home/", views.home_view, name="home"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

