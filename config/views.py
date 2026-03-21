from datetime import date

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.recipes.models import MenuDay

# ポートフォリオ画面
def top_view(request):
    return render(request, 'top.html')

# ホーム画面
@login_required
def home_view(request):
    today = date.today()

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