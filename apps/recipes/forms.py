from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
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
                    "class": "memo-textarea",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["recipe_name"].required = True
        self.fields["menu_category"].required = True
        self.fields["servings"].required = True

        self.fields["menu_category"].choices = [
        ("", "選択してください"),
        *self.fields["menu_category"].choices[1:]
        ]

        self.fields["servings"] = forms.ChoiceField(
            choices=[("", "-")] + [(i, i) for i in range(1, 101)],
            required=True
        )       
        
# レシピ材料
class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["food_item", "amount_text"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = self.fields["food_item"].queryset

        # 表示ラベルを書き換える
        choices = []
        for item in queryset:
            label = item.ingredient_name

            # よみがながあれば追加
            if item.reading_kana:
                label = f"{item.ingredient_name}"

            choices.append((item.id, label))

        self.fields["food_item"].choices = choices
        
    def clean_amount_text(self):
        amount_text = self.cleaned_data.get("amount_text", "")

        if not amount_text:
            return amount_text

        translated_text = amount_text.translate(
            str.maketrans(
                "０１２３４５６７８９／　",
                "0123456789/ "
            )
        )

        return translated_text.strip()

    def __init__(self, *args, **kwargs):
        self.recipe = kwargs.pop("recipe", None)
        super().__init__(*args, **kwargs)

        self.fields["amount_text"].widget.attrs["placeholder"] = "分量"
        self.fields["food_item"].empty_label = "材料選択"
        self.fields["food_item"].widget.attrs["class"] = "ingredient-select"
        
        self.fields["food_item"].queryset = FoodItem.objects.order_by("ingredient_name")

        self.fields["food_item"].label_from_instance = (
            lambda obj: f"{obj.ingredient_name}｜{obj.get_category_display()}"
        )

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
    
# 材料用のカスタムFormSet
class BaseRecipeIngredientFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_ingredient = False

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            food_item = form.cleaned_data.get("food_item")
            amount_text = form.cleaned_data.get("amount_text")

            if food_item and amount_text:
                has_ingredient = True

            if food_item and not amount_text:
                raise forms.ValidationError("材料の分量を入力してください")

            if amount_text and not food_item:
                raise forms.ValidationError("材料名を選択してください")

# 作り方
class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["instruction"]
        widgets = {
            "instruction": forms.Textarea(
                attrs={
                    "placeholder": "作り方を入力してください",
                    "rows": 3,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["food_item"].empty_label = "検索"
        self.fields["food_item"].queryset = FoodItem.objects.order_by("ingredient_name")
        self.fields["food_item"].widget.attrs["class"] = "home-food-select"
        self.fields["food_item"].widget.attrs["data-placeholder"] = "検索"

        self.fields["food_item"].label_from_instance = (
            lambda obj: (
                f"{obj.ingredient_name}｜{obj.get_category_display()}｜{obj.reading_kana}"
                if obj.reading_kana
                else f"{obj.ingredient_name}｜{obj.get_category_display()}"
            )
        )
        
        
# 食材マスタへの新規食材追加フォーム
class FoodItemCreateForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["ingredient_name", "category", "item_type"]

    def clean_ingredient_name(self):
        ingredient_name = self.cleaned_data["ingredient_name"].strip()
        ingredient_name = ingredient_name.replace("　", " ")

        if FoodItem.objects.filter(ingredient_name=ingredient_name).exists():
            raise forms.ValidationError("この食材名はすでに登録されています")

        return ingredient_name
            
# レシピ編集画面の食材追加用        
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=BaseRecipeIngredientFormSet,
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

