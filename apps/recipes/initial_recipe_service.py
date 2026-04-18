import csv
import os
from pathlib import Path

from django.conf import settings
from django.core.files import File

from .models import Recipe, RecipeIngredient, RecipeStep, FoodItem


INITIAL_RECIPE_NAMES = [
    "白ごはん",
    "かけうどん",
    "ハンバーグ",
    "ポテトサラダ",
    "きんぴらごぼう",
    "だし巻きたまご",
    "からあげ",
    "みそ汁",
    "たまごスープ",
]


def create_initial_recipes_for_user(user):
    """
    新規ユーザー用に初期レシピを登録する
    すでに同名レシピがある場合は二重登録しない
    """
    base_dir = Path(settings.BASE_DIR)

    recipes_csv_path = base_dir / "recipes.csv"
    ingredients_csv_path = base_dir / "recipe_ingredients.csv"
    steps_csv_path = base_dir / "recipe_steps.csv"
    image_dir = base_dir / "initial_recipe_images"

    if not recipes_csv_path.exists():
        raise FileNotFoundError(f"recipes.csv が見つかりません: {recipes_csv_path}")

    if not ingredients_csv_path.exists():
        raise FileNotFoundError(f"recipe_ingredients.csv が見つかりません: {ingredients_csv_path}")

    if not steps_csv_path.exists():
        raise FileNotFoundError(f"recipe_steps.csv が見つかりません: {steps_csv_path}")

    existing_names = set(
        Recipe.objects.filter(
            user=user,
            recipe_name__in=INITIAL_RECIPE_NAMES
        ).values_list("recipe_name", flat=True)
    )

    recipes = []
    with open(recipes_csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipes.append(row)

    ingredients = []
    with open(ingredients_csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ingredients.append(row)

    steps = []
    with open(steps_csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            steps.append(row)

    created_recipes = {}

    for row in recipes:
        recipe_name = row["recipe_name"].strip()

        if recipe_name in existing_names:
            continue

        recipe = Recipe.objects.create(
            user=user,
            recipe_name=recipe_name,
            menu_category=int(row["menu_category"]),
            servings=row.get("servings", "").strip(),
        )

        image_path_jpg = image_dir / f"{recipe_name}.jpg"
        image_path_png = image_dir / f"{recipe_name}.png"

        image_path = None
        if image_path_jpg.exists():
            image_path = image_path_jpg
        elif image_path_png.exists():
            image_path = image_path_png

        if image_path:
            with open(image_path, "rb") as image_file:
                recipe.image.save(
                    os.path.basename(image_path),
                    File(image_file),
                    save=True,
                )

        created_recipes[recipe_name] = recipe

    target_recipe_names = set(created_recipes.keys())

    for row in ingredients:
        recipe_name = row["recipe_name"].strip()

        if recipe_name not in target_recipe_names:
            continue

        recipe = created_recipes[recipe_name]

        ingredient_name = row["ingredient_name"].strip()
        amount_text = row["amount_text"].strip()

        food_item = FoodItem.objects.filter(
            ingredient_name=ingredient_name
        ).first()

        if not food_item:
            continue

        exists = RecipeIngredient.objects.filter(
            recipe=recipe,
            food_item=food_item,
        ).exists()

        if exists:
            continue

        RecipeIngredient.objects.create(
            recipe=recipe,
            food_item=food_item,
            amount_text=amount_text,
        )

    for row in steps:
        recipe_name = row["recipe_name"].strip()

        if recipe_name not in target_recipe_names:
            continue

        recipe = created_recipes[recipe_name]

        RecipeStep.objects.create(
            recipe=recipe,
            step_no=int(row["step_no"]),
            instruction=row["instruction"].strip(),
        )