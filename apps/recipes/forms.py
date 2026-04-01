from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient, RecipeStep, MenuDay, ShoppingListItem, HomeFoodItem, FoodItem

# レシピ
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "recipe_name",
            "menu_category",
            "servings",
            "image",
            "memo",
            "reference_url",
        ]
        widgets = {
            "recipe_name": forms.TextInput(
                attrs={"placeholder": "レシピ名入力"}
            ),
            "reference_url": forms.URLInput(
                attrs={"placeholder": "URL入力"}
            ),
            "memo": forms.Textarea(
                attrs={
                    "placeholder": "メモ入力",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["menu_category"].choices = [
        ("", "選択してください"),
        *self.fields["menu_category"].choices[1:]
    ]

        self.fields["servings"].widget = forms.Select(
            choices=[(i, i) for i in range(1, 101)]
    )
        
# レシピ材料
class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["food_item", "amount_text"]

    def __init__(self, *args, **kwargs):
        self.recipe = kwargs.pop("recipe", None)
        super().__init__(*args, **kwargs)

        self.fields["amount_text"].widget.attrs["placeholder"] = "分量入力"
        self.fields["food_item"].empty_label = "材料選択"

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
        fields = ["instruction"]
        widgets = {
            "instruction": forms.Textarea(
                attrs={
                    "placeholder": "作り方を入力してください",
                    "rows": 1,
                    "class": "step-textarea",
                }
            ),
        }

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
        fields = ["ingredient_name", "category", "item_type"]
        
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
    extra=1,  # 最初は1行だけ表示
    can_delete=True
)
