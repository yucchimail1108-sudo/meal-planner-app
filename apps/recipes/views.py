import calendar
from datetime import date

from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeIngredient, RecipeStep, Favorite, MenuDay, MenuSlot
from .forms import RecipeForm, RecipeIngredientForm, RecipeStepForm, MenuDayForm
from django.core.paginator import Paginator
from django.db.models import Q



# レシピ一覧画面
@login_required
def recipe_list_view(request):
    
    recipes = Recipe.objects.filter(user=request.user).order_by("id")
    
    selected_category = request.GET.get("category")
    search_query = request.GET.get("q")
   
    # 検索
    if search_query:
        recipes = recipes.filter(
            Q(recipe_name__icontains=search_query) |
            Q(ingredients__food_item__ingredient_name__icontains=search_query)
        ).distinct()
    
    # お気に入り
    if selected_category == "favorite":
        recipes = recipes.filter(favorite_set__user=request.user)
    
    # カテゴリ
    elif selected_category in ["1", "2", "3", "4"]:
        recipes = recipes.filter(menu_category=int(selected_category))

    # お気に入りID取得
    favorite_recipe_ids = set(
        Favorite.objects.filter(user=request.user).values_list("recipe_id", flat=True)
    )
    
    # ページネーション     
    paginator = Paginator(recipes, 5)
    page_number = request.GET.get("page")
    recipes = paginator.get_page(page_number)
            
    return render(
        request, 
        "recipes/recipe_list.html",
        {
            "recipes":recipes,
            "selected_category":selected_category,
            "favorite_recipe_ids": favorite_recipe_ids
        }
    )

# レシピ詳細画面
@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
        user=request.user
    )
    
    return render(
        request, 
        "recipes/recipe_detail.html", 
        {"recipe": recipe}
    )

# レシピ登録画面
@login_required
def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            return redirect('recipes:recipe_list')
    else:
        form = RecipeForm()
        
    return render(
        request,
        "recipes/recipe_form.html", 
        {"form": form}
    )

# レシピ編集画面
@login_required
def recipe_update_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
        user=request.user
    )

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect(
                'recipes:recipe_detail',
                recipe_id=recipe.id
            )
    else:
        form = RecipeForm(instance=recipe)
        
    return render(
        request,
        "recipes/recipe_form.html",
        {"form": form}
    )
    
# レシピ削除画面
@login_required
def recipe_delete_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
        user=request.user
    )

    if request.method == 'POST':
        recipe.delete()
        return redirect('recipes:recipe_list')
           
    return render(
        request, 
        "recipes/recipe_confirm_delete.html",
        {"recipe": recipe}
    )

# 材料追加
@login_required
def ingredient_create_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    
    if request.method == 'POST':
        form = RecipeIngredientForm(request.POST, recipe=recipe)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.recipe = recipe
            ingredient.save()
            return redirect(
                'recipes:recipe_detail',
                recipe_id=recipe.id
            )
    else:
        form = RecipeIngredientForm(recipe=recipe)
        
    return render(
        request,
        "recipes/ingredient_form.html",
        {"form": form,"recipe": recipe}
    )

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
           
    return redirect(
        "recipes:recipe_detail",
        recipe_id=recipe_id
    )

# 材料編集
@login_required
def ingredient_update_view(request, ingredient_id):
    ingredient = get_object_or_404(
        RecipeIngredient,
        id=ingredient_id,
        recipe__user=request.user
    )
    
    if request.method == 'POST':
        form = RecipeIngredientForm(
            request.POST,
            instance=ingredient,
            recipe=ingredient.recipe
            )
        if form.is_valid():
            form.save()
            return redirect(
                'recipes:recipe_detail',
                recipe_id=ingredient.recipe.id
            )
    else:
        form = RecipeIngredientForm(
            instance=ingredient,
            recipe=ingredient.recipe
            )
        
    return render(
        request, 
        "recipes/ingredient_form.html",
        {"form": form,"recipe": ingredient.recipe}
    )

# 作り方追加
@login_required
def step_create_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
        user=request.user
    )

    if request.method == "POST":
        form = RecipeStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.recipe = recipe
            step.save()
            return redirect("recipes:recipe_detail", recipe_id=recipe.id)
    else:
        form = RecipeStepForm()

    return render(
        request,
        "recipes/step_form.html",
        {"form": form, "recipe": recipe}
    )
    
# 作り方編集
@login_required
def step_update_view(request, step_id):
    step = get_object_or_404(
        RecipeStep,
        id=step_id,
        recipe__user=request.user
    )

    if request.method == "POST":
        form = RecipeStepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            return redirect("recipes:recipe_detail", recipe_id=step.recipe.id)
    else:
        form = RecipeStepForm(instance=step)

    return render(
        request,
        "recipes/step_form.html",
        {"form": form, "recipe": step.recipe}
    )
    
# 作り方削除
@login_required
def step_delete_view(request, step_id):
    step = get_object_or_404(
        RecipeStep,
        id=step_id,
        recipe__user=request.user
    )
    
    recipe_id = step.recipe.id
    step.delete()

    return redirect("recipes:recipe_detail", recipe_id=recipe_id)

# お気に入りトグル
@login_required
def favorite_toggle_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
        user=request.user
    )
    
    favorite = Favorite.objects.filter(
        user=request.user,
        recipe=recipe
    ).first()
    
    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(
            user=request.user,
            recipe=recipe
        )

    return redirect("recipes:recipe_list")

# 献立作成
@login_required
def menu_day_create_view(request):
    if request.method == "POST":
        form = MenuDayForm(request.POST)
        if form.is_valid():
            menu_day,created = MenuDay.objects.get_or_create(
                user=request.user,
                plan_date=form.cleaned_data["plan_date"],
                defaults={
                    "eat_out":form.cleaned_data["eat_out"],
                    "deli":form.cleaned_data["deli"],
                    "is_cooked": False,                   
                }
            )
    
            if not created:
                menu_day.eat_out = form.cleaned_data["eat_out"]
                menu_day.deli = form.cleaned_data["deli"]
                menu_day.save()
            
            for meal_type in ["staple", "main", "side", "soup"]:
                MenuSlot.objects.get_or_create(
                    menu_day=menu_day,
                    meal_type=meal_type
                )
                
            return redirect(
                "recipes:menu_detail",
                plan_date=menu_day.plan_date
            )
        
    else:
        form = MenuDayForm()
        
    return render(
        request,
        "recipes/menu_day_form.html",
        {"form": form}
    )

# 献立詳細
@login_required
def menu_day_detail_view(request, plan_date):
    menu_day = get_object_or_404(
        MenuDay,
        user=request.user,
        plan_date=plan_date
    )
    
    slots = {slot.meal_type: slot for slot in menu_day.slots.all()}
                   
    return render(
        request,
        "recipes/menu_day_detail.html",
        {
            "menu_day": menu_day,
            "slots": slots,
        }
    )

# 献立カレンダー
@login_required
def menu_calendar_view(request):
    
    today = date.today()
    
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    _, last_day = calendar.monthrange(year, month)
    
    menu_days = MenuDay.objects.filter(
        user=request.user,
        plan_date__year=year,
        plan_date__month=month
    )
    
    menu_day_dict = {
        menu_day.plan_date.day: menu_day
        for menu_day in menu_days
    }
    
    day_list = []
    for day in range(1, last_day + 1):
        day_list.append({
            "day":day,
            "menu_day": menu_day_dict.get(day)
        })
        
    context = {
        "year" : year,
        "month" : month,
        "day_list" : day_list,
    }
           
    return render(
        request,
        "recipes/menu_calendar.html",
        context
        )
