from django.db import models
from django.contrib.auth.models import User

# レシピ
class Recipe(models.Model):
    
    MENU_CATEGORY_CHOICES = [
        (1, "主食"),
        (2, "主菜"),
        (3, "副菜"),
        (4, "汁物"),
    ]
    
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
    
    menu_category = models.IntegerField(
        choices=MENU_CATEGORY_CHOICES,
        verbose_name="カテゴリ",
        null=True,
        blank=True
    )
    
    servings = models.PositiveIntegerField(
        verbose_name="作る量"
    )

    image = models.ImageField(
        upload_to="recipe_images/",
        blank=True,
        null=True,
        verbose_name="写真"
    )

    reference_url = models.URLField(
        blank=True,
        verbose_name="参照URL"
    )
        
    memo = models.TextField(
        blank=True,
        verbose_name="メモ"
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

# 食材
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

# レシピ材料
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
        

# 作り方
class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name="レシピ"
    )
     
    step_no = models.PositiveIntegerField(
         verbose_name="手順番号"         
     )
     
    instruction = models.TextField(
         verbose_name="手順内容" 
     )
         
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta:
        verbose_name = '作り方'
        verbose_name_plural = '作り方'
        constraints = [
            models.UniqueConstraint(
                fields=["recipe","step_no"],
                name="unique_recipe_step_no"
            )
        ]
        ordering = ["step_no"]
        
    def __str__(self):
        return f"{self.recipe} - 手順{self.step_no}"
    

# お気に入り
class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="ユーザー"
    )
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="レシピ",
        related_name="favorite_set"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
      
    class Meta:
        verbose_name = "お気に入り"
        verbose_name_plural = "お気に入り"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_favorite"
            )
        ]
        
    def __str__(self):
        return f"{self.user} - {self.recipe}"