from django.contrib import admin
from .models import Recipe, FoodItem, RecipeIngredient

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe_name", "user", "servings", "created_at")
    search_fields = ("recipe_name",)
    create_at = ("created_at",)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "ingredient_name", "category")
    search_fields = ("ingredient_name",)
    list_filter = ("category",)
    

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "food_item", "ingredient_kind", "amount_text", "created_at")
    search_fields = ("recipe__recipe_name", "food_item__ingredient_name", "amount_text")
    list_filter = ("ingredient_kind", "created_at")