from .models import MenuDay, MenuSlot

MEAL_TYPES = ["staple", "main", "side", "soup"]


def get_or_create_menu_day_with_slots(user, plan_date):
    """
    指定ユーザー・指定日付の献立を取得する
    なければ MenuDay を作成し 4枠の MenuSlot もそろえる
    """
    menu_day, _ = MenuDay.objects.get_or_create(
        user=user,
        plan_date=plan_date,
        defaults={
            "eat_out": False,
            "deli": False,
            "is_cooked": False,
        }
    )

    existing_meal_types = set(
        menu_day.slots.values_list("meal_type", flat=True)
    )

    for meal_type in MEAL_TYPES:
        if meal_type not in existing_meal_types:
            MenuSlot.objects.create(
                menu_day=menu_day,
                meal_type=meal_type,
            )

    menu_day = (
        MenuDay.objects
        .prefetch_related("slots__recipe")
        .get(id=menu_day.id)
    )

    return menu_day