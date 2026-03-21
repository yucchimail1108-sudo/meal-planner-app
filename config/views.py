from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.recipes.models import MenuDay, MenuSlot


# ポートフォリオ画面
def top_view(request):
    return render(request, "top.html")


# ホーム画面
@login_required
def home_view(request):
    today = date.today()

    if request.method == "POST":
        eat_out = "eat_out" in request.POST
        deli = "deli" in request.POST

        # 同時チェック禁止
        if eat_out and deli:
            messages.error(request, "外食と惣菜は同時に選択できません")
            return redirect("home")

        menu_day, created = MenuDay.objects.get_or_create(
            user=request.user,
            plan_date=today,
            defaults={
                "eat_out": False,
                "deli": False,
                "is_cooked": False,
            }
        )

        # スロット生成
        for meal_type in ["staple", "main", "side", "soup"]:
            MenuSlot.objects.get_or_create(
                menu_day=menu_day,
                meal_type=meal_type
            )

        # レシピが入っているかチェック
        slots = menu_day.slots.all()
        has_recipe = any(slot.recipe for slot in slots)

        if (eat_out or deli) and has_recipe:
            messages.error(
                request,
                "外食または惣菜を選択する場合は献立をすべて削除してください"
            )
            return redirect("home")

        # 保存
        menu_day.eat_out = eat_out
        menu_day.deli = deli
        menu_day.save()

        messages.success(request, "外食または惣菜の設定を保存しました")
        return redirect("home")

    menu_day = MenuDay.objects.filter(
        user=request.user,
        plan_date=today
    ).prefetch_related("slots__recipe").first()

    slot_dict = {}

    if menu_day:
        slot_dict = {
            slot.meal_type: slot
            for slot in menu_day.slots.all()
        }

    context = {
        "today": today,
        "menu_day": menu_day,
        "staple_slot": slot_dict.get("staple"),
        "main_slot": slot_dict.get("main"),
        "side_slot": slot_dict.get("side"),
        "soup_slot": slot_dict.get("soup"),
    }

    return render(request, "home.html", context)