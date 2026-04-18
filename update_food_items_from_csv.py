import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.recipes.models import FoodItem


csv_path = "food_items_update.csv"

updated_count = 0
not_found_ids = []
error_rows = []

with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        try:
            item_id = int(row["id"])
            ingredient_name = row["ingredient_name"].strip()
            reading_kana = row["reading_kana"].strip()
            category = int(row["category"])
            item_type = int(row["item_type"])

            food_item = FoodItem.objects.filter(id=item_id).first()

            if not food_item:
                not_found_ids.append(item_id)
                continue

            food_item.ingredient_name = ingredient_name
            food_item.reading_kana = reading_kana
            food_item.category = category
            food_item.item_type = item_type
            food_item.save()

            updated_count += 1

        except Exception as e:
            error_rows.append({
                "row": row,
                "error": str(e),
            })

print("=== 更新結果 ===")
print(f"更新件数: {updated_count}")

if not_found_ids:
    print("見つからなかったID:")
    for item_id in not_found_ids:
        print(item_id)

if error_rows:
    print("エラー行:")
    for error in error_rows:
        print(error)