from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path("", views.recipe_list_view, name="recipe_list"),
    path("menu/", views.menu_day_create_view, name="menu_create"),
    path("menu/calendar/", views.menu_calendar_view, name="menu_calendar"),
    path("menu/slot/<int:slot_id>/edit/", views.menu_slot_update_view, name="menu_slot_update"),
    path("menu/<str:plan_date>/edit/", views.menu_day_update_view, name="menu_update"),
    path("menu/<str:plan_date>/", views.menu_day_detail_view, name="menu_detail"),
    path("create/", views.recipe_create_view, name="recipe_create"),
    path("<int:recipe_id>/favorite/", views.favorite_toggle_view, name="favorite_toggle"),
    path("<int:recipe_id>/ingredient/add/", views.ingredient_create_view, name="ingredient_create"),
    path("<int:recipe_id>/edit/", views.recipe_update_view, name="recipe_update"),
    path("<int:recipe_id>/delete/", views.recipe_delete_view, name="recipe_delete"),
    path("<int:recipe_id>/step/add/", views.step_create_view, name="step_create"),
    path("<int:recipe_id>/", views.recipe_detail_view, name="recipe_detail"),
    path("ingredient/<int:ingredient_id>/delete/", views.ingredient_delete_view, name="ingredient_delete"),
    path("ingredient/<int:ingredient_id>/edit/", views.ingredient_update_view, name="ingredient_update"),
    path("step/<int:step_id>/edit/", views.step_update_view, name="step_update"),
    path("step/<int:step_id>/delete/", views.step_delete_view, name="step_delete"),
    path("shopping-list/", views.shopping_list_view, name="shopping_list"),
    path("shopping-list/<int:item_id>/delete/", views.shopping_list_delete_view, name="shopping_list_delete"),
]
