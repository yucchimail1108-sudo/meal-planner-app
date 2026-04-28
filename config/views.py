from datetime import date, datetime, timedelta


from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.recipes.models import MenuDay, MenuSlot, Recipe
from apps.recipes.services import get_or_create_menu_day_with_slots

# ポートフォリオ画面
def top_view(request):
    return render(request, "portfolio.html")


# ホーム画面
@login_required
def home_view(request):
    selected_date_str = request.GET.get("date")

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = date.today()

    if request.method == "POST":
        clear_menu_mode = request.POST.get("clear_menu_mode")

        if clear_menu_mode:
            menu_day = get_or_create_menu_day_with_slots(request.user, selected_date)
            menu_day.eat_out = False
            menu_day.deli = False
            menu_day.save()

            messages.success(request, "外食・惣菜の設定を解除しました")
            return redirect(f"/home/?date={selected_date}")

        delete_slot_id = request.POST.get("delete_slot_id")

        if delete_slot_id:
            slot = MenuSlot.objects.filter(
                id=delete_slot_id,
                menu_day__user=request.user
            ).first()

            if slot:
                meal_label_map = {
                    "staple": "主食",
                    "main": "主菜",
                    "side": "副菜",
                    "soup": "汁物",
                }

                label = meal_label_map.get(slot.meal_type, "献立")

                slot.recipe = None
                slot.save()

                temp_menu = request.session.get("temp_menu", {})
                temp_menu.pop(str(slot.id), None)
                request.session["temp_menu"] = temp_menu

                messages.success(request, f"{label}を削除しました")
            else:
                messages.error(request, "削除対象の献立が見つかりません")

            return redirect(f"{reverse('home')}?date={selected_date}")

        eat_out = "eat_out" in request.POST
        deli = "deli" in request.POST

        if eat_out and deli:
            messages.error(request, "外食と惣菜は同時に選択できません")
            return redirect(f"/home/?date={selected_date}")

        menu_day = get_or_create_menu_day_with_slots(request.user, selected_date)

        slots = list(menu_day.slots.all())

        temp_menu = request.session.get("temp_menu", {})

        has_saved_recipe = any(slot.recipe for slot in slots)
        has_temp_recipe = any(temp_menu.get(str(slot.id)) for slot in slots)

        if eat_out or deli:
            # 保存済みレシピ削除
            for slot in slots:
                slot.recipe = None
                slot.save()

            # 仮選択も削除
            request.session["temp_menu"] = {}

        menu_day.eat_out = eat_out
        menu_day.deli = deli
        menu_day.save()

        if not eat_out and not deli:
            for slot in slots:
                temp_recipe_id = temp_menu.get(str(slot.id))

                if temp_recipe_id:
                    recipe = Recipe.objects.filter(
                        id=temp_recipe_id,
                        user=request.user
                    ).first()
                    slot.recipe = recipe
                    slot.save()

        request.session["temp_menu"] = {}

        messages.success(request, "献立を保存しました")
        return redirect(f"{reverse('home')}?date={selected_date}")

    menu_day = get_or_create_menu_day_with_slots(request.user, selected_date)

    slot_dict = {}

    if menu_day:
        slot_dict = {
            slot.meal_type: slot
            for slot in menu_day.slots.all()
        }

    temp_menu = request.session.get("temp_menu", {})

    temp_recipe_map = {}

    for slot_name in ["staple", "main", "side", "soup"]:
        slot = slot_dict.get(slot_name)

        if not slot:
            temp_recipe_map[slot_name] = None
            continue

        temp_recipe_id = temp_menu.get(str(slot.id))

        if temp_recipe_id:
            temp_recipe_map[slot_name] = Recipe.objects.filter(
                id=temp_recipe_id,
                user=request.user
            ).first()
        else:
            temp_recipe_map[slot_name] = None

    has_saved_recipe = any(
        slot and slot.recipe
        for slot in slot_dict.values()
    )

    has_temp_recipe = any(
        recipe is not None
        for recipe in temp_recipe_map.values()
    )

    has_today_menu = (
        has_saved_recipe
        or has_temp_recipe
        or (menu_day and menu_day.eat_out)
        or (menu_day and menu_day.deli)
    )

    context = {
        "today": selected_date,
        "menu_day": menu_day,
        "staple_slot": slot_dict.get("staple"),
        "main_slot": slot_dict.get("main"),
        "side_slot": slot_dict.get("side"),
        "soup_slot": slot_dict.get("soup"),
        "temp_staple_recipe": temp_recipe_map.get("staple"),
        "temp_main_recipe": temp_recipe_map.get("main"),
        "temp_side_recipe": temp_recipe_map.get("side"),
        "temp_soup_recipe": temp_recipe_map.get("soup"),
        "has_temp_recipe": has_temp_recipe,
        "has_today_menu": has_today_menu,
        "prev_date": selected_date - timedelta(days=1),
        "next_date": selected_date + timedelta(days=1),
    }

    return render(request, "home.html", context)