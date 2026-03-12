from django.shortcuts import render, get_object_or_404
from .models import Recipe

def recipe_list_view(request):
    recipes = Recipe.objects.all()

    return render(
        request,
        "recipes/recipe_list.html",
        {"recipes":recipes}    
    )
    
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id    
    )
    
    return render(
        request,
        "recipes/recipe_detail.html",
        {"recipe": recipe}
    )