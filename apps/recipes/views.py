from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe
from .forms import RecipeForm

# レシピ一覧画面
@login_required
def recipe_list_view(request):
    recipes = Recipe.objects.filter(user=request.user)
    
    return render(request, "recipes/recipe_list.html", {"recipes":recipes})

# レシピ詳細画面
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe,id=recipe_id)
    
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})

# 登録画面
@login_required
def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            return redirect('recipes:recipe_list')
    else:
        form = RecipeForm()
        
    return render(request, "recipes/recipe_form.html", {"form": form})

# 編集画面
def recipe_update_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipes:recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
        
    return render(request, "recipes/recipe_form.html", {"form": form})
    
# 削除画面
def recipe_delete_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        recipe.delete()
        return redirect('recipes:recipe_list')
           
    return render(request, "recipes/recipe_confirm_delete.html", {"recipe": recipe})