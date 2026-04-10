import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.recipes.models import FoodItem

# CSVファイルパス
CSV_PATH = "食材マスタ更新.csv"

updated_count = 0
not_found = []

with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        ingredient_name = row["食材名"]
        reading_kana = row["よみがな"]

        try:
            food = FoodItem.objects.get(ingredient_name=ingredient_name)
            food.reading_kana = reading_kana
            food.save()
            updated_count += 1
        except FoodItem.DoesNotExist:
            not_found.append(ingredient_name)

print(f"更新件数: {updated_count}")

if not_found:
    print("見つからなかった食材:")
    for name in not_found:
        print(f"- {name}")