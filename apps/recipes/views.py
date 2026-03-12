from django.shortcuts import render
from .models import Recipe

def recipe_list_view(request):
    recipes = Recipe.objects.all()

    return render(
        request,
        "recipes/recipe_list.html",
        {"recipes":recipes}    
    )
    