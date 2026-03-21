from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.recipes.models import MenuDay, MenuSlot

# ポートフォリオ画面
def top_view(request):
    return render(request, 'top.html')

# ホーム画面
@login_required
def home_view(request):
    today = date.today()

    if request.method == "POST":
        menu_day, created = MenuDay.objects.get_or_create(
            user=request.user,
            plan_date=today,
            defaults={
                "eat_out": False,
                "deli": False,
                "is_cooked": False,
            }
        )

        menu_day.eat_out = "eat_out" in request.POST
        menu_day.deli = "deli" in request.POST
        menu_day.save()

        for meal_type in ["staple", "main", "side", "soup"]:
            MenuSlot.objects.get_or_create(
                menu_day=menu_day,
                meal_type=meal_type
            )

        messages.success(request, "外食・惣菜の設定を保存しました。")
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