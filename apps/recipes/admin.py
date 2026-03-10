from django.contrib import admin
from .models import Recipe, FoodItem, RecipeIngredient

admin.site.register(Recipe)
admin.site.register(FoodItem)
admin.site.register(RecipeIngredient)
