import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.recipes.models import FoodItem

CATEGORY_MAP = {
    "青果": 1,
    "魚・肉": 2,
    "常温": 3,
    "冷蔵": 4,
    "主食": 5,
    "冷凍": 6,
    "その他": 7,
}

ITEM_TYPE_MAP = {
    "食材": 1,
    "調味料ほか": 2,
}

created_count = 0

with open("食材マスタ.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        name = row["食材名"].strip()
        category_str = row["カテゴリ"].strip()
        item_type_str = row["種別"].strip()

        if not name:
            continue

        category = CATEGORY_MAP.get(category_str)
        item_type = ITEM_TYPE_MAP.get(item_type_str)

        if category is None:
            print(f"カテゴリ不明: {category_str}")
            continue

        if item_type is None:
            print(f"種別不明: {item_type_str}")
            continue

        obj, created = FoodItem.objects.get_or_create(
            ingredient_name=name,
            defaults={
                "category": category,
                "item_type": item_type,
            }
        )

        if created:
            created_count += 1

print(f"追加件数: {created_count}")