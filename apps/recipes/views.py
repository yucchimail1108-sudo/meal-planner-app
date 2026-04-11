import calendar
from datetime import date, datetime, timedelta
import re
from decimal import Decimal, InvalidOperation
from django.urls import reverse

from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeIngredient, RecipeStep, Favorite, MenuDay, MenuSlot, ShoppingListItem, HomeFoodItem, FoodItem
from .forms import RecipeForm, RecipeIngredientForm, RecipeStepForm, MenuDayForm, ShoppingListItemForm, ShoppingListExtractForm, HomeFoodItemForm, FoodItemCreateForm, RecipeIngredientFormSet, RecipeStepFormSet
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
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

    base_recipes = Recipe.objects.filter(user=request.user)

    recipes = base_recipes.order_by("-id")

    selected_category = request.GET.get("category", "")
    search_query = request.GET.get("q", "").strip()

    category_counts = {
        "all": base_recipes.count(),
        "staple": base_recipes.filter(menu_category=1).count(),
        "main": base_recipes.filter(menu_category=2).count(),
        "side": base_recipes.filter(menu_category=3).count(),
        "soup": base_recipes.filter(menu_category=4).count(),
        "favorite": Favorite.objects.filter(user=request.user).count(),
    }

    if search_query:
        recipes = recipes.filter(
            Q(recipe_name__icontains=search_query) |
            Q(ingredients__food_item__ingredient_name__icontains=search_query)
        ).distinct()

    if selected_category == "favorite":
        recipes = recipes.filter(favorite_set__user=request.user)
    elif selected_category in ["1", "2", "3", "4"]:
        recipes = recipes.filter(menu_category=int(selected_category))

    favorite_recipe_ids = set(
        Favorite.objects.filter(user=request.user).values_list("recipe_id", flat=True)
    )

    return render(
        request,
        "recipes/recipe_list.html",
        {
            "recipes": recipes,
            "selected_category": selected_category,
            "favorite_recipe_ids": favorite_recipe_ids,
            "category_counts": category_counts,
        }
    )
    
# 分量換算
def convert_amount_text(amount_text, scale):
    text = amount_text.strip()
    
    # 全角数字を半角数字に変換
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    # 全角スラッシュを半角スラッシュに変換
    text = text.replace("／", "/")

    def format_decimal(value):
        if value % 1 == 0:
            return str(int(value))
        return str(value.normalize())

    def format_mixed_fraction(value):
        integer_part = int(value)
        fraction_part = value - Decimal(integer_part)

        if fraction_part == 0:
            return str(integer_part)

        fraction_map = {
            Decimal("0.25"): "1/4",
            Decimal("0.3333333333"): "1/3",
            Decimal("0.5"): "1/2",
            Decimal("0.6666666667"): "2/3",
            Decimal("0.75"): "3/4",
        }

        rounded_fraction = fraction_part.quantize(Decimal("0.0000000001"))

        matched_fraction = None
        for decimal_value, fraction_text in fraction_map.items():
            if rounded_fraction == decimal_value:
                matched_fraction = fraction_text
                break

        if matched_fraction:
            if integer_part == 0:
                return matched_fraction
            return f"{integer_part}と{matched_fraction}"

        if integer_part == 0:
            return format_decimal(value)
        return format_decimal(value)

    # ① 単位 + 分数付き 例: 大さじ1/2
    unit_fraction_match = re.match(r"^(.*?)(\d+)\s*/\s*(\d+)$", text)
    if unit_fraction_match:
        prefix_text = unit_fraction_match.group(1)
        numerator = Decimal(unit_fraction_match.group(2))
        denominator = Decimal(unit_fraction_match.group(3))

        try:
            base_value = numerator / denominator
            converted = base_value * scale
        except (InvalidOperation, ZeroDivisionError):
            return amount_text

        return f"{prefix_text}{format_mixed_fraction(converted)}"

    # ② 分数が先頭にある場合 例: 1/2個
    fraction_match = re.match(r"^(\d+)\s*/\s*(\d+)(.*)$", text)
    if fraction_match:
        numerator = Decimal(fraction_match.group(1))
        denominator = Decimal(fraction_match.group(2))
        unit_text = fraction_match.group(3)

        try:
            base_value = numerator / denominator
            converted = base_value * scale
        except (InvalidOperation, ZeroDivisionError):
            return amount_text

        return f"{format_mixed_fraction(converted)}{unit_text}"

    # ③ 数字が末尾にある場合 例: 大さじ1 / 小さじ2
    suffix_number_match = re.match(r"^(.*?)(\d+(?:\.\d+)?)$", text)
    if suffix_number_match:
        prefix_text = suffix_number_match.group(1)
        number_text = suffix_number_match.group(2)

        try:
            converted = Decimal(number_text) * scale
        except InvalidOperation:
            return amount_text

        return f"{prefix_text}{format_decimal(converted)}"

    # ④ 数字が先頭にある場合 例: 500cc / 150g
    prefix_number_match = re.match(r"^(\d+(?:\.\d+)?)(.*)$", text)
    if prefix_number_match:
        number_text = prefix_number_match.group(1)
        unit_text = prefix_number_match.group(2)

        try:
            converted = Decimal(number_text) * scale
        except InvalidOperation:
            return amount_text

        return f"{format_decimal(converted)}{unit_text}"

    # ⑤ 数字がない場合 例: 適量
    return amount_text

# レシピ詳細画面
@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
        user=request.user
    )

    scale_text = request.GET.get("scale", "1")

    try:
        scale = Decimal(scale_text)
    except InvalidOperation:
        scale = Decimal("1")
        scale_text = "1"

    ingredients = recipe.ingredients.all()

    converted_ingredients = []
    for ingredient in ingredients:
        converted_ingredients.append({
            "ingredient": ingredient,
            "converted_amount": convert_amount_text(
                ingredient.amount_text,
                scale
            )
        })

    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "recipe": recipe,
            "scale": scale_text,
            "converted_ingredients": converted_ingredients,
        }
    )

# 材料未入力で保存できないようにする
def has_valid_ingredient_input(ingredient_formset):
    for form in ingredient_formset.forms:
        if not hasattr(form, "cleaned_data"):
            continue

        if not form.cleaned_data:
            continue

        if form.cleaned_data.get("DELETE"):
            continue

        food_item = form.cleaned_data.get("food_item")
        amount_text = form.cleaned_data.get("amount_text")

        if food_item and amount_text:
            return True

    return False


# レシピ登録画面
@login_required
def recipe_create_view(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        ingredient_formset = RecipeIngredientFormSet(
            request.POST,
            prefix="ingredients"
        )
        step_formset = RecipeStepFormSet(
            request.POST,
            prefix="steps"
        )

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            if not has_valid_ingredient_input(ingredient_formset):
                messages.error(request, "材料を1件以上入力してください")
            else:
                recipe = form.save(commit=False)
                recipe.user = request.user
                recipe.save()

                ingredient_formset.instance = recipe
                ingredient_formset.save()

                step_formset.instance = recipe
                step_objects = step_formset.save(commit=False)

                for index, step in enumerate(step_objects, start=1):
                    step.recipe = recipe
                    step.step_no = index
                    step.save()

                return redirect(
                    "recipes:recipe_detail",
                    recipe_id=recipe.id
                )
    else:
        form = RecipeForm()
        ingredient_formset = RecipeIngredientFormSet(prefix="ingredients")
        step_formset = RecipeStepFormSet(prefix="steps")

    return render(
        request,
        "recipes/recipe_form.html",
        {
            "form": form,
            "ingredient_formset": ingredient_formset,
            "step_formset": step_formset,
        }
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
        ingredient_formset = RecipeIngredientFormSet(
            request.POST,
            instance=recipe,
            prefix="ingredients"
        )
        step_formset = RecipeStepFormSet(
            request.POST,
            instance=recipe,
            prefix="steps"
        )

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            if not has_valid_ingredient_input(ingredient_formset):
                messages.error(request, "材料を1件以上入力してください")
            else:
                form.save()
                ingredient_formset.save()

                for step_form in step_formset.deleted_forms:
                    if step_form.instance.pk:
                        step_form.instance.delete()

                step_number = 1

                for step_form in step_formset.forms:
                    if step_form in step_formset.deleted_forms:
                        continue

                    if not hasattr(step_form, "cleaned_data"):
                        continue

                    if not step_form.cleaned_data:
                        continue

                    instruction = step_form.cleaned_data.get("instruction")
                    if not instruction:
                        continue

                    step = step_form.save(commit=False)
                    step.recipe = recipe
                    step.step_no = step_number
                    step.save()

                    step_number += 1

                return redirect(
                    "recipes:recipe_detail",
                    recipe_id=recipe.id
                )

            for step_form in step_formset.deleted_forms:
                if step_form.instance.pk:
                    step_form.instance.delete()

            step_number = 1

            for step_form in step_formset.forms:
                if step_form in step_formset.deleted_forms:
                    continue

                if not hasattr(step_form, "cleaned_data"):
                    continue

                if not step_form.cleaned_data:
                    continue

                instruction = step_form.cleaned_data.get("instruction")
                if not instruction:
                    continue

                step = step_form.save(commit=False)
                step.recipe = recipe
                step.step_no = step_number
                step.save()

                step_number += 1

            return redirect(
                "recipes:recipe_detail",
                recipe_id=recipe.id
            )
    else:
        form = RecipeForm(instance=recipe)
        ingredient_formset = RecipeIngredientFormSet(
            instance=recipe,
            prefix="ingredients"
        )
        step_formset = RecipeStepFormSet(
            instance=recipe,
            prefix="steps"
        )

    return render(
        request,
        "recipes/recipe_form.html",
        {
            "form": form,
            "recipe": recipe,
            "ingredient_formset": ingredient_formset,
            "step_formset": step_formset,
        }
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

            last_step = RecipeStep.objects.filter(recipe=recipe).count()
            step.step_no = last_step + 1

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

    slot_map = {
        "staple": None,
        "main": None,
        "side": None,
        "soup": None,
    }

    if menu_day:
        for slot in menu_day.slots.all():
            slot_map[slot.meal_type] = slot

        has_recipe = any(slot.recipe for slot in menu_day.slots.all())

        can_delete_menu = (
            has_recipe
            or menu_day.eat_out
            or menu_day.deli
        )

        is_empty_menu_day = (
            not has_recipe
            and not menu_day.eat_out
            and not menu_day.deli
        )
    else:
        can_delete_menu = False
        is_empty_menu_day = True

    prev_date = target_date - timedelta(days=1)
    next_date = target_date + timedelta(days=1)

    return render(
        request,
        "recipes/menu_day_detail.html",
        {
            "menu_day": menu_day,
            "slots": slot_map,
            "target_date": target_date,
            "prev_date": prev_date,
            "next_date": next_date,
            "can_delete_menu": can_delete_menu,
            "is_empty_menu_day": is_empty_menu_day,
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
            print("ここ通ってる:", menu_day.plan_date)
            return redirect(f"{reverse('home')}?date={menu_day.plan_date}")

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
        recipes = recipes.filter(
            Q(recipe_name__icontains=q) |
            Q(ingredients__food_item__ingredient_name__icontains=q) |
            Q(ingredients__food_item__reading_kana__icontains=q)
        ).distinct()

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
        
        if plan_date:
            return redirect(f"/home/?date={plan_date}")
        
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
    ).prefetch_related(
        "slots__recipe"
    ).first()

    if not menu_day:
        messages.error(request, "選択した日の献立が見つかりません")
        return redirect("recipes:menu_calendar")
    
    if menu_day.is_cooked:
        messages.error(request, "その日はすでに調理済みです")
        return redirect("recipes:menu_calendar")


    selected_recipes = []

    for slot in menu_day.slots.all():
        if slot.recipe:
            selected_recipes.append(slot.recipe)

    if not selected_recipes:
        messages.error(
            request,
            "レシピが登録されている日のみ、つくった！を登録できます"
        )
        return redirect("recipes:menu_calendar")

    recipe_ingredients = RecipeIngredient.objects.filter(
        recipe__in=selected_recipes
    ).select_related("food_item", "recipe")

    # 食材のみ対象（調味料は除外）
    target_ingredients = [
        ingredient
        for ingredient in recipe_ingredients
        if ingredient.food_item.item_type == FoodItem.ITEM_TYPE_CHOICES[0][0]
    ]

    ingredient_food_item_ids = [
        ingredient.food_item_id
        for ingredient in target_ingredients
    ]

    home_food_items = HomeFoodItem.objects.filter(
        user=request.user,
        food_item_id__in=ingredient_food_item_ids
    ).select_related("food_item")

    deleted_food_names = sorted(list({
        home_food_item.food_item.ingredient_name
        for home_food_item in home_food_items
    }))

    with transaction.atomic():
        menu_day.is_cooked = True
        menu_day.save()
        home_food_items.delete()

    if deleted_food_names:
        deleted_food_names_text = "、".join(deleted_food_names)
        messages.success(
            request,
            f"おうち食材から減らしました：{deleted_food_names_text}"
        )
    else:
        messages.success(
            request,
            "つくった！を登録しました（減らしたおうち食材はありません）"
        )
    return redirect("recipes:menu_calendar")

# おうち食材を一括削除
@login_required
def home_food_bulk_delete_view(request):
    if request.method != "POST":
        return redirect("recipes:home_food_list")

    selected_ids = request.POST.getlist("selected_items")

    if not selected_ids:
        messages.info(request, "削除する食材を選択してください")
        return redirect("recipes:home_food_list")

    target_items = HomeFoodItem.objects.filter(
        user=request.user,
        id__in=selected_ids
    ).select_related("food_item")

    deleted_names = [
        item.food_item.ingredient_name
        for item in target_items
    ]

    deleted_count = target_items.count()
    target_items.delete()

    if deleted_count == 0:
        messages.info(request, "削除対象の食材が見つかりませんでした")
    else:
        deleted_names_text = "、".join(deleted_names)
        messages.success(
            request,
            f"おうち食材から削除しました：{deleted_names_text}"
        )

    return redirect("recipes:home_food_list")

# 買い物リスト一覧＆追加＆購入済み処理
@login_required
def shopping_list_view(request):
    # ログインユーザーの買い物リストを取得
    shopping_items = ShoppingListItem.objects.filter(
        user=request.user
    ).select_related("food_item").order_by(
        "food_item__category",
        "food_item__ingredient_name"
    )

    # 買い物リスト追加フォームを先に用意
    form = ShoppingListItemForm(request.POST or None)

    # 抽出期間フォームを用意
    extract_form = ShoppingListExtractForm()
    
    if request.method == "POST":
        action = request.POST.get("action")

        # 購入済み処理
        if action == "mark_as_purchased":
            checked_ids = request.POST.getlist("checked_items")

            added_home_food_names = []
            removed_condiment_names = []

            for item_id in checked_ids:
                item = get_object_or_404(
                    ShoppingListItem,
                    id=item_id,
                    user=request.user
                )

                food_item = item.food_item

                # 食材だけおうち食材に追加
                if food_item.item_type == 1:
                    exists = HomeFoodItem.objects.filter(
                        user=request.user,
                        food_item=food_item
                    ).exists()

                    if not exists:
                        HomeFoodItem.objects.create(
                            user=request.user,
                            food_item=food_item
                        )

                    added_home_food_names.append(food_item.ingredient_name)

                # 調味料はおうち食材に追加しない
                elif food_item.item_type == 2:
                    removed_condiment_names.append(food_item.ingredient_name)

                # どちらも買い物リストから削除
                item.delete()

            if added_home_food_names and removed_condiment_names:
                added_names_text = "、".join(added_home_food_names)
                removed_names_text = "、".join(removed_condiment_names)
                messages.success(
                    request,
                    f"購入済み食材（{added_names_text}）をおうち食材に追加し、調味料（{removed_names_text}）を買い物リストから削除しました"
                )
            elif added_home_food_names:
                added_names_text = "、".join(added_home_food_names)
                messages.success(
                    request,
                    f"購入済み食材（{added_names_text}）を、おうち食材に追加しました"
                )
            elif removed_condiment_names:
                removed_names_text = "、".join(removed_condiment_names)
                messages.success(
                    request,
                    f"購入済み調味料（{removed_names_text}）を、買い物リストから削除しました"
                )
            else:
                messages.info(request, "購入済みの食材を選択してください")

            return redirect("recipes:shopping_list")

        # 手動追加処理
        elif action == "manual_add":
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
                    messages.success(
                        request,
                        f"買い物リストに追加しました：{shopping_item.food_item.ingredient_name}"
                    )
                else:
                    messages.info(
                        request,
                        "すでに登録されている食材です"
                    )

                return redirect("recipes:shopping_list")

            messages.error(request, "手動追加フォームの入力内容を確認してください")
            shopping_items = ShoppingListItem.objects.filter(
                user=request.user
            ).select_related("food_item").order_by(
                "food_item__category",
                "food_item__ingredient_name"
            )

            extract_form = ShoppingListExtractForm()

            return render(
                request,
                "recipes/shopping_list.html",
                {
                    "shopping_items": shopping_items,
                    "form": form,
                    "extract_form": extract_form,
                }
            )

        # 不明なPOST
        else:
            messages.error(request, "不正な操作です")
            return redirect("recipes:shopping_list")
 
# 抽出処理（GETで日付が来た場合）
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if request.method == "GET" and start_date and end_date:
        extract_form = ShoppingListExtractForm(request.GET)

        if extract_form.is_valid():
            start_date = extract_form.cleaned_data["start_date"]
            end_date = extract_form.cleaned_data["end_date"]

            # 指定期間の献立を取得
            menu_days = MenuDay.objects.filter(
                user=request.user,
                plan_date__range=[start_date, end_date]
            )

            # 献立に設定されているレシピIDを重複なしで取得
            recipe_ids = MenuSlot.objects.filter(
                menu_day__in=menu_days,
                recipe__isnull=False
            ).values_list("recipe_id", flat=True).distinct()

            # レシピ材料を取得
            ingredients = RecipeIngredient.objects.filter(
                recipe_id__in=recipe_ids
            ).select_related("food_item")

            # 調味料を除いた food_item を重複なしでまとめる
            target_food_items = {}

            for ingredient in ingredients:
                food_item = ingredient.food_item

                # 調味料は除外
                if food_item.item_type == 2:
                    continue

                target_food_items[food_item.id] = food_item

            # おうち食材にある food_item_id 一覧
            home_food_item_ids = set(
                HomeFoodItem.objects.filter(
                    user=request.user
                ).values_list("food_item_id", flat=True)
            )

            # すでに買い物リストにある food_item_id 一覧
            existing_shopping_item_ids = set(
                ShoppingListItem.objects.filter(
                    user=request.user
                ).values_list("food_item_id", flat=True)
            )

            added_food_names = []

            for food_item_id, food_item in target_food_items.items():
                if food_item_id in home_food_item_ids:
                    continue

                if food_item_id in existing_shopping_item_ids:
                    continue

                ShoppingListItem.objects.create(
                    user=request.user,
                    food_item=food_item
                )
                added_food_names.append(food_item.ingredient_name)

            if not added_food_names:
                messages.info(
                    request,
                    "追加対象の食材はありませんでした（すでに買い物リストにあるか、おうち食材にあります）"
                )
            else:
                added_names_text = "、".join(added_food_names)
                messages.success(
                    request,
                    f"買い物リストに追加しました：{added_names_text}"
                )

            # 抽出後の買い物リストを取り直す
            shopping_items = ShoppingListItem.objects.filter(
                user=request.user
            ).select_related("food_item").order_by(
                "food_item__category",
                "food_item__ingredient_name"
            )

    # GETパラメータがあれば、それをフォームに渡す
    if request.GET.get("start_date") and request.GET.get("end_date"):
        extract_form = ShoppingListExtractForm(request.GET)
    else:
        extract_form = ShoppingListExtractForm()

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
                home_food_item = form.save(commit=False)
                home_food_item.user = request.user

                exists = HomeFoodItem.objects.filter(
                    user=request.user,
                    food_item=home_food_item.food_item
                ).exists()

                if not exists:
                    home_food_item.save()
                    messages.success(
                        request,
                        f"{home_food_item.food_item.ingredient_name}をおうち食材に追加しました"
                    )
                else:
                    messages.info(
                        request,
                        "この食材はすでにおうち食材に登録されています。"
                    )

                return redirect("recipes:home_food_list")

            messages.error(request, "入力内容を確認してください")

        # 新規食材を作成して追加する処理
        elif action == "add_new_food":
            create_form = FoodItemCreateForm(request.POST)
            form = HomeFoodItemForm()

            if create_form.is_valid():
                ingredient_name = create_form.cleaned_data["ingredient_name"]
                category = create_form.cleaned_data["category"]
                item_type = create_form.cleaned_data["item_type"]

                food_item, created = FoodItem.objects.get_or_create(
                    ingredient_name=ingredient_name,
                    category=category,
                    defaults={
                        "item_type": item_type,
                    }
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

            messages.error(request, "新規食材の入力内容を確認してください")

        else:
            form = HomeFoodItemForm()
            create_form = FoodItemCreateForm()
            messages.error(request, "不正な操作です")

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

# 食材マスタ新規登録（レシピ登録画面から使う用）
@login_required
def food_item_create_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "recipes:recipe_create"
    
    # モーダルのfetchから来た通信かどうか判定
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if request.method == "POST":
        form = FoodItemCreateForm(request.POST)

        if form.is_valid():
            ingredient_name = form.cleaned_data["ingredient_name"]
            category = form.cleaned_data["category"]
            item_type = form.cleaned_data["item_type"]

            food_item, created = FoodItem.objects.get_or_create(
                ingredient_name=ingredient_name,
                defaults={
                    "category": category,
                    "item_type": item_type,
                }
            )
            
            # モーダル追加ならJSONで返す
            if is_ajax:
                category_label = food_item.get_category_display()
                label = f"{food_item.ingredient_name}｜{category_label}"

                return JsonResponse(
                    {
                        "success": True,
                        "food_item": {
                            "id": food_item.id,
                            "name": food_item.ingredient_name,
                            "label": label,
                        },
                    }
                )

            # 画面遷移版は今まで通り
            if created:
                messages.success(request, f"{food_item.ingredient_name}を食材マスタに追加しました")
            else:
                messages.info(request, "この食材はすでに登録されています")

            return redirect(next_url)
 
        # モーダル追加でエラーならJSONで返す   
        if is_ajax:
            error_messages = []
            for field_errors in form.errors.values():
                error_messages.extend(field_errors)

            return JsonResponse(
                {
                    "success": False,
                    "error": " / ".join(error_messages) if error_messages else "入力内容を確認してください",
                },
                status=400,
            )
                
    else:
        form = FoodItemCreateForm()

    return render(
        request,
        "recipes/food_item_form.html",
        {
            "form": form,
            "next": next_url,
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