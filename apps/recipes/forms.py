from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient, RecipeStep, MenuDay, ShoppingListItem, HomeFoodItem, FoodItem

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

# 買い物リスト追加用フォーム
class ShoppingListItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingListItem
        fields = ["food_item"]
        
# 買い物リスト抽出期間入力用フォーム
class ShoppingListExtractForm(forms.Form):
    start_date = forms.DateField(
        label="開始日",
        widget=forms.DateInput(attrs={"type": "date"})
    )
    end_date = forms.DateField(
        label="終了日",
        widget=forms.DateInput(attrs={"type": "date"})
    )

# おうち食材追加フォーム
class HomeFoodItemForm(forms.ModelForm):
    class Meta:
        model = HomeFoodItem
        fields = ["food_item"]
        
        
# 食材マスタへの新規食材追加フォーム
class FoodItemCreateForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["ingredient_name", "category"]
        
# レシピ編集画面の食材追加用        
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True
)

# レシピ編集画面の作り方追加用        
RecipeStepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    form=RecipeStepForm,
    extra=2, # 最初から作り方を2行出す
    can_delete=True
)