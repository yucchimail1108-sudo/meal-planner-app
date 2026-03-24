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


def get_menu_day_with_slots(user, plan_date):
    """
    指定ユーザー・指定日付の献立を取得する
    存在しない場合は None を返す
    存在する場合は 4枠の MenuSlot をそろえて返す
    """
    menu_day = (
        MenuDay.objects
        .filter(user=user, plan_date=plan_date)
        .prefetch_related("slots__recipe")
        .first()
    )

    if not menu_day:
        return None

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

# レシピ在りの場合、外食・惣菜を同時に保存できない
def validate_menu_day(menu_day):
    
    slots = menu_day.slots.all()
    has_recipe = any(slot.recipe for slot in slots)

    if (menu_day.eat_out or menu_day.deli) and has_recipe:
        return False

    return True

# カレンダー上で表示対象の献立か判定する
def has_visible_menu(menu_day):

    slots = menu_day.slots.all()
    has_recipe = any(slot.recipe for slot in slots)

    return has_recipe or menu_day.eat_out or menu_day.deli