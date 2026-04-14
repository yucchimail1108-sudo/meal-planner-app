from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.top_view, name='top'),
    path('home/', views.home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('recipes/', include('apps.recipes.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)