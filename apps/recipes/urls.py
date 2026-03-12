from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path("", views.recipe_list_view, name="recipe_list"),
    path("<int:recipe_id>", views.recipe_detail_view, name="recipe_detail"),
]
