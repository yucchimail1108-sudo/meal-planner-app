import calendar
from datetime import date

from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeIngredient, RecipeStep, Favorite, MenuDay, MenuSlot, ShoppingListItem, HomeFoodItem
from .forms import RecipeForm, RecipeIngredientForm, RecipeStepForm, MenuDayForm, ShoppingListItemForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages


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
                "recipes:menu_update",
                plan_date=menu_day.plan_date
            )
    
    #「作成する」を押したとき、その日付が最初から入るようにする    
    else: 
        initial = {}
        plan_date = request.GET.get("plan_date")
        if plan_date:
            initial["plan_date"] = plan_date
        
        form = MenuDayForm(initial=initial)
        
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

# 献立編集
@login_required
def menu_day_update_view(request, plan_date):
    menu_day = get_object_or_404(
        MenuDay,
        user=request.user,
        plan_date=plan_date
    )
    
    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["plan_date"] = menu_day.plan_date.strftime("%Y-%m-%d")
        
        form = MenuDayForm(post_data, instance=menu_day)
        
        if form.is_valid():
            form.save()
            messages.success(request, "献立を保存しました")
            return redirect(
                "recipes:menu_update",
                plan_date=menu_day.plan_date
            )
            
    else:
        form = MenuDayForm(initial={
            'plan_date': menu_day.plan_date,
            'eat_out': menu_day.eat_out,
            'deli': menu_day.deli,
        })
        
    return render(
        request,
        "recipes/menu_day_edit.html",
        {
            "form": form,
            "menu_day":menu_day,
            "slots": menu_day.slots.all(),
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
        full_date = f"{year}-{month:02d}-{day:02d}"
                
        day_list.append({
            "day":day,
            "full_date": full_date,
            "menu_day": menu_day_dict.get(day)
        })
    
    # 「前月」「次月」の年月を作る処理
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1
    
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
        
        
    context = {
        "year" : year,
        "month" : month,
        "day_list" : day_list,
        "prev_year" : prev_year,
        "prev_month" : prev_month,
        "next_year" : next_year,
        "next_month" : next_month,
    }
           
    return render(
        request,
        "recipes/menu_calendar.html",
        context
        )

# 献立レシピ設定
@login_required
def menu_slot_update_view(request, slot_id):
    
    slot = get_object_or_404(
        MenuSlot,
        id=slot_id,
        menu_day__user=request.user
    )
    
    recipes = Recipe.objects.filter(user=request.user)
    
    if request.method == "POST":
        
        recipe_id = request.POST.get("recipe_id")
        
        if recipe_id:
            slot.recipe = get_object_or_404(
                Recipe,
                id=recipe_id,
                user=request.user
            )
        else:
            slot.recipe = None

        slot.save()
        
        return redirect(
            "recipes:menu_update",
            plan_date=slot.menu_day.plan_date
        )

    return render(
        request,
        "recipes/menu_slot_form.html",
        {
            "slot": slot,
            "recipes": recipes,
        }
    )

# 買い物リスト一覧＆追加＆購入済み処理
@login_required
def shopping_list_view(request):
    shopping_items = ShoppingListItem.objects.filter(
        user=request.user
    ).select_related("food_item")

    if request.method == "POST":

        # チェックされたIDを取得
        checked_ids = request.POST.getlist("checked_items")

        # 購入済み処理
        if checked_ids:
            for item_id in checked_ids:
                item = ShoppingListItem.objects.get(
                    id=item_id,
                    user=request.user
                )

                # おうち食材に追加（重複防止）
                exists = HomeFoodItem.objects.filter(
                    user=request.user,
                    food_item=item.food_item
                ).exists()

                if not exists:
                    HomeFoodItem.objects.create(
                        user=request.user,
                        food_item=item.food_item
                    )

                # 買い物リストから削除
                item.delete()

            return redirect("recipes:shopping_list")

        # 追加処理（今までの処理）
        form = ShoppingListItemForm(request.POST)
        if form.is_valid():
            shopping_item = form.save(commit=False)
            shopping_item.user = request.user

            exists = ShoppingListItem.objects.filter(
                user=request.user,
                food_item=shopping_item.food_item
            ).exists()

            if not exists:
                shopping_item.save()

            return redirect("recipes:shopping_list")

    else:
        form = ShoppingListItemForm()

    return render(
        request,
        "recipes/shopping_list.html",
        {
            "shopping_items": shopping_items,
            "form": form,
        }
    )
    
# 買い物リスト1件を削除する画面処理
@login_required
def shopping_list_delete_view(request, item_id):
    # ログインユーザーの買い物リスト1件を取得
    shopping_item = get_object_or_404(
        ShoppingListItem,
        id=item_id,
        user=request.user
    )

    # POST送信のときだけ削除する
    if request.method == "POST":
        shopping_item.delete()
        return redirect("recipes:shopping_list")

    return redirect("recipes:shopping_list")