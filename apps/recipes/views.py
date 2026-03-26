import calendar
from datetime import date, datetime, timedelta

from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeIngredient, RecipeStep, Favorite, MenuDay, MenuSlot, ShoppingListItem, HomeFoodItem, FoodItem
from .forms import RecipeForm, RecipeIngredientForm, RecipeStepForm, MenuDayForm, ShoppingListItemForm, ShoppingListExtractForm, HomeFoodItemForm, FoodItemCreateForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .services import (
    get_or_create_menu_day_with_slots,
    get_menu_day_with_slots,
    validate_menu_day,
    has_visible_menu,
)

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
    target_date = datetime.strptime(plan_date, "%Y-%m-%d").date()

    menu_day = get_menu_day_with_slots(request.user, target_date)

    if not menu_day:
        messages.error(request, "献立が存在しません")
        return redirect("recipes:menu_calendar")

    slot_map = {
        "staple": None,
        "main": None,
        "side": None,
        "soup": None,
    }

    for slot in menu_day.slots.all():
        slot_map[slot.meal_type] = slot

    can_delete_menu = (
        any(slot.recipe for slot in menu_day.slots.all())
        or menu_day.eat_out
        or menu_day.deli
    )

    prev_date = menu_day.plan_date - timedelta(days=1)
    next_date = menu_day.plan_date + timedelta(days=1)

    return render(
        request,
        "recipes/menu_day_detail.html",
        {
            "menu_day": menu_day,
            "slots": slot_map,
            "target_date": menu_day.plan_date,
            "prev_date": prev_date,
            "next_date": next_date,
            "can_delete_menu": can_delete_menu,
        }
    )

# 献立編集
@login_required
def menu_day_update_view(request, plan_date):
    target_date = datetime.strptime(plan_date, "%Y-%m-%d").date()
    menu_day = get_or_create_menu_day_with_slots(request.user, target_date)

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["plan_date"] = menu_day.plan_date.strftime("%Y-%m-%d")

        form = MenuDayForm(post_data, instance=menu_day)

        if form.is_valid():
            updated_menu_day = form.save(commit=False)

            # 同時チェック禁止
            if updated_menu_day.eat_out and updated_menu_day.deli:
                messages.error(request, "外食と惣菜は同時に選択できません")
                return redirect(
                    "recipes:menu_update",
                    plan_date=menu_day.plan_date
                )

            # レシピあり + 外食/惣菜 の排他チェック
            if not validate_menu_day(updated_menu_day):
                messages.error(
                    request,
                    "外食または惣菜を選択する場合は献立をすべて削除してください"
                )
                return redirect(
                    "recipes:menu_update",
                    plan_date=menu_day.plan_date
                )

            updated_menu_day.save()
            messages.success(request, "献立を保存しました")
            return redirect(
                "recipes:menu_update",
                plan_date=menu_day.plan_date
            )

    else:
        form = MenuDayForm(initial={
            "plan_date": menu_day.plan_date,
            "eat_out": menu_day.eat_out,
            "deli": menu_day.deli,
        })

    return render(
        request,
        "recipes/menu_day_edit.html",
        {
            "form": form,
            "menu_day": menu_day,
            "slots": menu_day.slots.all(),
        }
    )
    
# 献立削除
@login_required
def menu_day_delete_view(request, plan_date):
    target_date = datetime.strptime(plan_date, "%Y-%m-%d").date()

    menu_day = get_object_or_404(
        MenuDay,
        user=request.user,
        plan_date=target_date
    )

    if request.method == "POST":
        menu_day.delete()
        messages.success(request, "献立を削除しました")
        return redirect("recipes:menu_calendar")

    return render(
        request,
        "recipes/menu_day_confirm_delete.html",
        {"menu_day": menu_day}
    )

# その日の献立から 表示用の料理名リストを作る関数
def build_calendar_meal_items(menu_day):
    meal_items = []

    if not menu_day:
        return meal_items

    slot_dict = {
        slot.meal_type: slot
        for slot in menu_day.slots.all()
    }

    meal_labels = {
        "staple": "主食",
        "main": "主菜",
        "side": "副菜",
        "soup": "汁物",
    }

    for meal_type in ["staple", "main", "side", "soup"]:
        slot = slot_dict.get(meal_type)
        if slot and slot.recipe:
            meal_items.append(
                f"{meal_labels[meal_type]}：{slot.recipe.recipe_name}"
            )

    return meal_items

def build_calendar_day_data(day_date, month, menu_day):
    meal_items = build_calendar_meal_items(menu_day)

    visible = False
    if menu_day:
        visible = has_visible_menu(menu_day)

    return {
        "date": day_date,
        "day": day_date.day,
        "is_current_month": (day_date.month == month),
        "menu_day": menu_day,
        "is_cooked": menu_day.is_cooked if menu_day else False,
        "has_visible_menu": visible,
        "meal_items": meal_items,
        "has_more_meals": len(meal_items) > 2,
        "display_meal_items": meal_items[:2],
    }

# 献立カレンダー
@login_required
def menu_calendar_view(request):
    today = date.today()

    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    cal = calendar.Calendar(firstweekday=6)
    month_dates = cal.monthdatescalendar(year, month)

    menu_days = MenuDay.objects.filter(
        user=request.user,
        plan_date__year=year,
        plan_date__month=month
    ).prefetch_related("slots__recipe")

    menu_day_dict = {
        menu_day.plan_date: menu_day
        for menu_day in menu_days
    }

    calendar_weeks = []
    for week in month_dates:
        week_data = []

        for day_date in week:
            menu_day = menu_day_dict.get(day_date)

            week_data.append(
                build_calendar_day_data(
                    day_date=day_date,
                    month=month,
                    menu_day=menu_day,
                )
            )

        calendar_weeks.append(week_data)

    # 前月
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    # 次月
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    context = {
        "year": year,
        "month": month,
        "calendar_weeks": calendar_weeks,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "today": date.today(),
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

    meal_type_to_category = {
        "staple": 1,
        "main": 2,
        "side": 3,
        "soup": 4,
    }

    target_category = meal_type_to_category.get(slot.meal_type)

    q = request.GET.get("q", "").strip()

    recipes = Recipe.objects.filter(
        user=request.user,
        menu_category=target_category
    )

    if q:
        recipes = recipes.filter(recipe_name__icontains=q)

    recipes = recipes.order_by("-id")

    if request.method == "POST":
        recipe_id = request.POST.get("recipe_id")
        source = request.POST.get("source")
        plan_date = request.POST.get("plan_date")

        # 献立保存画面から来た場合は その日のslotへ直接保存
        if source == "menu_update":
            if recipe_id:
                slot.recipe = get_object_or_404(
                    Recipe,
                    id=recipe_id,
                    user=request.user
                )
            else:
                slot.recipe = None

            slot.save()

            messages.success(request, "レシピを設定しました")
            return redirect(
                "recipes:menu_update",
                plan_date=slot.menu_day.plan_date
            )

        # ホーム画面から来た場合は 仮保存
        temp_menu = request.session.get("temp_menu", {})
        temp_menu[str(slot.id)] = recipe_id
        request.session["temp_menu"] = temp_menu

        messages.success(request, "レシピを選択しました")
        return redirect("home")

    source = request.GET.get("source", "")
    plan_date = request.GET.get("plan_date", "")

    return render(
        request,
        "recipes/menu_slot_form.html",
        {
            "slot": slot,
            "recipes": recipes,
            "source": source,
            "plan_date": plan_date,
            "q": q,
        }
    )

# 献立レシピ削除
@login_required
def menu_slot_delete_view(request, slot_id):
    slot = get_object_or_404(
        MenuSlot,
        id=slot_id,
        menu_day__user=request.user
    )

    if request.method == "POST":
        slot.recipe = None
        slot.save()
        messages.success(request, "献立からレシピを削除しました")
        return redirect("home")

    return redirect("home")

# 献立の「つくった！」機能
@login_required
def menu_cooked_view(request):
    if request.method != "POST":
        return redirect("recipes:menu_calendar")

    cooked_date = request.POST.get("cooked_date")

    if not cooked_date:
        messages.error(request, "日付を選択してください")
        return redirect("recipes:menu_calendar")

    if cooked_date > str(date.today()):
        messages.error(request, "未来の日付は選択できません")
        return redirect("recipes:menu_calendar")

    menu_day = MenuDay.objects.filter(
        user=request.user,
        plan_date=cooked_date,
    ).first()

    if not menu_day:
        messages.error(request, "選択した日の献立が見つかりません")
        return redirect("recipes:menu_calendar")
    
    if menu_day.is_cooked:
        messages.error(request, "その日はすでに調理済みです")
        return redirect("recipes:menu_calendar")

    menu_day.is_cooked = True
    menu_day.save()

    messages.success(request, "つくった日を登録しました")
    return redirect("recipes:menu_calendar")


# 買い物リスト一覧＆追加＆購入済み処理
@login_required
def shopping_list_view(request):
    # ログインユーザーの買い物リストを取得
    shopping_items = ShoppingListItem.objects.filter(
        user=request.user
    ).select_related("food_item")

    # 買い物リスト追加フォームを先に用意
    form = ShoppingListItemForm(request.POST or None)

    # 抽出期間フォームを用意
    extract_form = ShoppingListExtractForm()
    
    if request.method == "POST":
        action = request.POST.get("action")

        # 購入済み処理
        if action == "mark_as_purchased":
            checked_ids = request.POST.getlist("checked_items")

            for item_id in checked_ids:
                item = get_object_or_404(
                    ShoppingListItem,
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
            messages.success(request, "購入済みの食材は、おうち食材へ追加しました")
            return redirect("recipes:shopping_list")

        # 追加処理
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
 
 # 抽出処理（GETで日付が来た場合）
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        # 指定期間の献立を取得
        menu_days = MenuDay.objects.filter(
            user=request.user,
            plan_date__range=[start_date, end_date]
        )

        # 献立枠を取得
        menu_slots = MenuSlot.objects.filter(
            menu_day__in=menu_days
        ).select_related("recipe")

        # レシピID一覧（None除外・重複除外）
        recipe_ids = list({
            slot.recipe.id for slot in menu_slots if slot.recipe
        })

        # レシピ食材取得
        ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=recipe_ids
        ).select_related("food_item")

        # 食材IDの重複を除外
        food_item_ids = list({
            ingredient.food_item.id for ingredient in ingredients
        })

        # そのユーザーのおうち食材ID一覧を取得
        home_food_item_ids = set(
            HomeFoodItem.objects.filter(
                user=request.user
            ).values_list("food_item_id", flat=True)
        )
        # まだ買い物リストに無く、かつおうち食材にも無い食材だけ追加
        added_count = 0

        for food_item_id in food_item_ids:
            
            # おうち食材にあるなら追加しない
            if food_item_id in home_food_item_ids:
                continue

            exists = ShoppingListItem.objects.filter(
                user=request.user,
                food_item_id=food_item_id
            ).exists()
            
            if not exists:
                ShoppingListItem.objects.create(
                    user=request.user,
                    food_item_id=food_item_id
                )
                added_count += 1
        
        if added_count == 0:
            messages.info(request, "追加対象の食材はありませんでした（すでに買い物リストにあるか、おうち食材にあります）。")
        else:
            messages.success(request, f"{added_count}件の食材を買い物リストに追加しました。")

        return redirect("recipes:shopping_list")


    return render(
        request,
        "recipes/shopping_list.html",
        {
            "shopping_items": shopping_items,
            "form": form,
             "extract_form": extract_form,
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


# おうち食材一覧画面
@login_required
def home_food_list_view(request):
    # おうち食材の追加処理
    if request.method == "POST":
        action = request.POST.get("action")

        # 既存食材を選んで追加する処理
        if action == "add_existing_food":
            form = HomeFoodItemForm(request.POST)
            create_form = FoodItemCreateForm()

            if form.is_valid():
                home_food = form.save(commit=False)
                home_food.user = request.user

                exists = HomeFoodItem.objects.filter(
                    user=request.user,
                    food_item=home_food.food_item
                ).exists()

                if not exists:
                    home_food.save()
                    messages.success(request, "おうち食材に追加しました")
                else:
                    messages.info(request, "この食材はすでに登録されています")

                return redirect("recipes:home_food_list")

        # 新規食材を作成して追加する処理
        elif action == "add_new_food":
            create_form = FoodItemCreateForm(request.POST)
            form = HomeFoodItemForm()

            if create_form.is_valid():
                ingredient_name = create_form.cleaned_data["ingredient_name"]
                category = create_form.cleaned_data["category"]

                food_item, created = FoodItem.objects.get_or_create(
                    ingredient_name=ingredient_name,
                    defaults={"category": category}
                )

                exists = HomeFoodItem.objects.filter(
                    user=request.user,
                    food_item=food_item
                ).exists()

                if not exists:
                    HomeFoodItem.objects.create(
                        user=request.user,
                        food_item=food_item
                    )
                    messages.success(request, "新しい食材を追加し、おうち食材にも登録しました。")
                else:
                    messages.info(request, "この食材はすでにおうち食材に登録されています。")

                return redirect("recipes:home_food_list")

        else:
            form = HomeFoodItemForm()
            create_form = FoodItemCreateForm()

    else:
        form = HomeFoodItemForm()
        create_form = FoodItemCreateForm()

    selected_category = request.GET.get("category")
    
    search_query = request.GET.get("q", "").strip()

    # ログインユーザーのおうち食材を取得
    home_food_items = HomeFoodItem.objects.filter(
        user=request.user
    ).select_related("food_item").order_by(
        "food_item__category",
        "food_item__ingredient_name"
    )

    if search_query:
        home_food_items = home_food_items.filter(
            food_item__ingredient_name__icontains=search_query
        )
    
    if selected_category:
        home_food_items = home_food_items.filter(
            food_item__category=int(selected_category)
        )

    return render(
        request,
        "recipes/home_food_list.html",
        {
            "home_food_items": home_food_items,
            "form": form,
            "create_form": create_form,
            "selected_category": selected_category,
            "search_query": search_query,
        }
    )
    
    
# おうち食材1件を削除する画面処理
@login_required
def home_food_delete_view(request, item_id):
    # ログインユーザーのおうち食材1件を取得
    home_food_item = get_object_or_404(
        HomeFoodItem,
        id=item_id,
        user=request.user
    )

    # POST送信のときだけ削除する
    if request.method == "POST":
        home_food_item.delete()
        messages.success(request, "おうち食材から削除しました")
        return redirect("recipes:home_food_list")

    return redirect("recipes:home_food_list")