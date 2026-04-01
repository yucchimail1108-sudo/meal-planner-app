from django.contrib import admin
from .models import Recipe, FoodItem, RecipeIngredient, RecipeStep, Favorite, MenuDay, MenuSlot, ShoppingListItem, HomeFoodItem

# レシピ管理画面
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe_name", "menu_category","user", "servings", "created_at")
    search_fields = ("recipe_name",)
    date_hierarchy = "created_at"

# 食材管理画面
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "ingredient_name", "category")
    search_fields = ("ingredient_name",)
    list_filter = ("category",)
    
# レシピ食材管理画面
@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "food_item", "food_item_type_display", "amount_text", "created_at")
    search_fields = ("recipe__recipe_name", "food_item__ingredient_name", "amount_text")
    list_filter = ("food_item__item_type", "created_at")

    @admin.display(description="食材種別")
    def food_item_type_display(self, obj):
        return obj.food_item.get_item_type_display()
    
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
    
# 献立（日）管理画面
@admin.register(MenuDay)
class MenuDayAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "plan_date", "eat_out", "deli", "is_cooked", "created_at")
    search_fields = ("user__username",)
    list_filter = ("plan_date", "eat_out", "deli", "is_cooked", "created_at")

# 献立（枠）管理画面
@admin.register(MenuSlot)
class MenuSlotAdmin(admin.ModelAdmin):
    list_display = ("id", "menu_day", "meal_type", "recipe", "created_at")
    search_fields = ("menu_day__plan_date", "recipe__recipe_name")
    list_filter = ("meal_type", "created_at")
    
# 買い物リスト画面
admin.site.register(ShoppingListItem)


# おうち食材管理画面
@admin.register(HomeFoodItem)
class HomeFoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "food_item", "created_at")
    search_fields = ("user__username", "food_item__ingredient_name")
    list_filter = ("created_at",)