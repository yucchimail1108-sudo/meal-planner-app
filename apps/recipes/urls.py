from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path("", views.recipe_list_view, name="recipe_list"),
    path("create/", views.recipe_create_view, name="recipe_create"),
    path("<int:recipe_id>/ingredient/add/", views.ingredient_create_view, name="ingredient_create"),
    path("<int:recipe_id>/edit/", views.recipe_update_view, name="recipe_update"),
    path("<int:recipe_id>/delete/", views.recipe_delete_view, name="recipe_delete"),
    path("<int:recipe_id>", views.recipe_detail_view, name="recipe_detail"),
    path("ingredient/<int:ingredient_id>/delete/", views.ingredient_delete_view, name="ingredient_delete"),
    path("ingredient/<int:ingredient_id>/edit/", views.ingredient_update_view, name="ingredient_update"),
]
