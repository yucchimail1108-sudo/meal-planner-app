from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path("", views.recipe_list_view, name="recipe_list"),
    path("create/", views.recipe_create_view, name="recipe_create"),
    path("<int:recipe_id>/edit/", views.recipe_update_view, name="recipe_update"),
    path("<int:recipe_id>", views.recipe_detail_view, name="recipe_detail"),
]
