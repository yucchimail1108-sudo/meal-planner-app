from django import forms
from .models import Recipe, RecipeIngredient, RecipeStep, MenuDay

# レシピ
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'recipe_name',
            'menu_category',
            'servings',
            'image',
            'memo',
            'reference_url'
            ]
        
# レシピ材料
class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["food_item", "ingredient_kind", "amount_text"]
    
    def __init__(self, *args, **kwargs):
        self.recipe = kwargs.pop("recipe", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        food_item = cleaned_data.get("food_item")

        if self.recipe and food_item:
            qs = RecipeIngredient.objects.filter(
                recipe=self.recipe,
                food_item=food_item
            )

            # 編集時は自分自身を除外
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError("この食材はすでに登録されています。")

        return cleaned_data    

# 作り方    
class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["step_no", "instruction"]

# 献立
class MenuDayForm(forms.ModelForm):
    class Meta:
        model = MenuDay
        fields = ["plan_date", "eat_out", "deli"]
        widgets = {
            "plan_date": forms.DateInput(attrs={"type": "date"}),
        }