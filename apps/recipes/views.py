from django.shortcuts import render, get_object_or_404,redirect
from .models import Recipe
from .forms import RecipeForm

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

def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recipes:recipe_list')
    else:
        form = RecipeForm()
        
    return render(
        request,
        "recipes/recipe_form.html",
        {"form": form}
    )