from django.contrib import admin
from .models import Recipe, FoodItem, RecipeIngredient, RecipeStep, Favorite

# レシピ管理画面
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe_name", "menu_category","user", "servings", "created_at")
    search_fields = ("recipe_name",)
    create_at = ("created_at",)

# 食材管理画面
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "ingredient_name", "category")
    search_fields = ("ingredient_name",)
    list_filter = ("category",)
    
# レシピ食材管理画面
@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "food_item", "ingredient_kind", "amount_text", "created_at")
    search_fields = ("recipe__recipe_name", "food_item__ingredient_name", "amount_text")
    list_filter = ("ingredient_kind", "created_at")
    
# 作り方管理画面
@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "step_no", "instruction", "created_at")
    search_fields = ("recipe__recipe_name", "instruction")
    list_filter = ("created_at",)

#お気に入り管理画面
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__recipe_name")
    list_filter = ("created_at",)