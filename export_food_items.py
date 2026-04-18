import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.recipes.models import FoodItem


output_path = "food_items_export.csv"

with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "ingredient_name", "reading_kana", "category", "item_type"])

    for item in FoodItem.objects.order_by("id"):
        writer.writerow([
            item.id,
            item.ingredient_name,
            item.reading_kana,
            item.category,
            item.item_type,
        ])

print(f"書き出し完了: {output_path}")