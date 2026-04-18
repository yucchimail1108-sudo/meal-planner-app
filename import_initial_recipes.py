import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from apps.recipes.models import Recipe, RecipeIngredient, RecipeStep, FoodItem

# ===== 対象ユーザー（自分のIDに変更）=====
USER_ID = 8

user = User.objects.get(id=USER_ID)

# ===== 既存の初期レシピを削除してから入れ直す =====
initial_recipe_names = [
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

Recipe.objects.filter(
    user=user,
    recipe_name__in=initial_recipe_names
).delete()

# ===== CSV読み込み =====
recipes = []
with open("recipes.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        recipes.append(row)

ingredients = []
with open("recipe_ingredients.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ingredients.append(row)

steps = []
with open("recipe_steps.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        steps.append(row)

# ===== レシピ作成 =====
created_recipes = []

for r in recipes:
    recipe = Recipe.objects.create(
        user=user,
        recipe_name=r["recipe_name"].strip(),
        menu_category=int(r["menu_category"]),
        servings=r.get("servings", "").strip(),
    )
    created_recipes.append(recipe)

# ===== 材料作成 =====
for ing in ingredients:
    recipe_name = ing["recipe_name"].strip()
    ingredient_name = ing["ingredient_name"].strip()
    amount_text = ing["amount_text"].strip()

    recipe = next(
        (r for r in created_recipes if r.recipe_name == recipe_name),
        None
    )

    if not recipe:
        print(f"レシピが見つからない: {recipe_name}")
        continue

    food_item = FoodItem.objects.filter(
        ingredient_name=ingredient_name
    ).first()

    if not food_item:
        print(f"食材が見つからない: {ingredient_name}")
        continue

    exists = RecipeIngredient.objects.filter(
        recipe=recipe,
        food_item=food_item
    ).exists()

    if exists:
        print(f"重複スキップ: {recipe.recipe_name} - {food_item.ingredient_name}")
        continue

    RecipeIngredient.objects.create(
        recipe=recipe,
        food_item=food_item,
        amount_text=amount_text,
    )

# ===== 作り方作成 =====
for st in steps:
    recipe_name = st["recipe_name"].strip()
    step_no = int(st["step_no"])
    instruction = st["instruction"].strip()

    recipe = next(
        (r for r in created_recipes if r.recipe_name == recipe_name),
        None
    )

    if not recipe:
        print(f"レシピが見つからない: {recipe_name}")
        continue

    RecipeStep.objects.create(
        recipe=recipe,
        step_no=step_no,
        instruction=instruction,
    )

print("初期レシピ投入完了")