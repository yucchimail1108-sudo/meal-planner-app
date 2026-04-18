import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from apps.recipes.models import Recipe
from django.core.files import File

# ===== 設定 =====
USER_ID = 8  # ←自分のIDにしてる前提
IMAGE_DIR = "initial_recipe_images"

user = User.objects.get(id=USER_ID)

updated_count = 0
not_found = []

for recipe in Recipe.objects.filter(user=user):
    image_path_jpg = os.path.join(IMAGE_DIR, f"{recipe.recipe_name}.jpg")
    image_path_png = os.path.join(IMAGE_DIR, f"{recipe.recipe_name}.png")

    image_path = None

    if os.path.exists(image_path_jpg):
        image_path = image_path_jpg
    elif os.path.exists(image_path_png):
        image_path = image_path_png

    if not image_path:
        not_found.append(recipe.recipe_name)
        continue

    with open(image_path, "rb") as f:
        recipe.image.save(os.path.basename(image_path), File(f), save=True)

    updated_count += 1

print("=== 結果 ===")
print(f"画像更新件数: {updated_count}")

if not_found:
    print("画像が見つからなかったレシピ:")
    for name in not_found:
        print(name)