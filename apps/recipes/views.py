from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeIngredient
from .forms import RecipeForm, RecipeIngredientForm

# レシピ一覧画面
@login_required
def recipe_list_view(request):
    recipes = Recipe.objects.filter(user=request.user)
    
    return render(request, "recipes/recipe_list.html", {"recipes":recipes})

# レシピ詳細画面
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe,id=recipe_id)
    
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})

# レシピ登録画面
@login_required
def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            return redirect('recipes:recipe_list')
    else:
        form = RecipeForm()
        
    return render(request, "recipes/recipe_form.html", {"form": form})

# レシピ編集画面
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
    
# レシピ削除画面
def recipe_delete_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        recipe.delete()
        return redirect('recipes:recipe_list')
           
    return render(request, "recipes/recipe_confirm_delete.html", {"recipe": recipe})

# 材料追加
@login_required
def ingredient_create_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    
    if request.method == 'POST':
        form = RecipeIngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.recipe = recipe
            ingredient.save()
            return redirect('recipes:recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeIngredientForm()
        
    return render(request, "recipes/ingredient_form.html", {"form": form, "recipe": recipe,})

# 材料削除
@login_required
def ingredient_delete_view(request, ingredient_id):
    ingredient = get_object_or_404(
        RecipeIngredient, 
        id=ingredient_id,
        recipe__user=request.user
    )

    recipe_id = ingredient.recipe.id
    ingredient.delete()
           
    return redirect("recipes:recipe_detail", recipe_id=recipe_id)