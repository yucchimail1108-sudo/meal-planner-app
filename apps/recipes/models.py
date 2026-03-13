from django.db import models
from django.contrib.auth.models import User

# レシピモデル
class Recipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="ユーザー",
        null=True,
        blank=True
    ) 
    recipe_name = models.CharField(
        max_length=100,
        verbose_name="レシピ名"
    )
    servings = models.PositiveIntegerField(
        verbose_name="作る量"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日"
    )
    
    def __str__(self):
        return self.recipe_name

    class Meta:
        verbose_name = "レシピ"
        verbose_name_plural = "レシピ"

# 食材モデル
class FoodItem(models.Model):
    
    CATEGORY_CHOICES = [
        (1, "青果"),
        (2, "魚/肉"),
        (3, "常温"),
        (4, "冷蔵"),
        (5, "主食"),
        (6, "冷凍"),
        (7, "その他"),
    ]
    
    ingredient_name = models.CharField(max_length=30, verbose_name="食材名")
    category = models.IntegerField(choices=CATEGORY_CHOICES, verbose_name="カテゴリ")
    
    def __str__(self):
        return self.ingredient_name
    
    class Meta:
        verbose_name = "食材"
        verbose_name_plural = "食材"

# レシピ材料モデル
class RecipeIngredient(models.Model):
    
    INGREDIENT_KIND_CHOICES = [
        (0, "食材"),
        (1, "調味料"),
    ]
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="レシピ"
    )
     
    food_item = models.ForeignKey(
         FoodItem,
         on_delete=models.CASCADE,
         verbose_name="食材"         
     )
     
    ingredient_kind = models.IntegerField(
         choices=INGREDIENT_KIND_CHOICES,
         default=0,
         verbose_name="材料区分"
     )
     
    amount_text = models.CharField(
         max_length=32,
         verbose_name="分量"
     )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recipe} - {self.food_item}"

    class Meta:
        verbose_name = 'レシピ材料'
        verbose_name_plural = 'レシピ材料'
        constraints = [
            models.UniqueConstraint(
                fields=["recipe","food_item"],
                name="unique_recipe_food_item"
            )
        ]
        
