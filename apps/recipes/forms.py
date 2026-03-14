from django import forms
from .models import Recipe, RecipeIngredient, RecipeStep


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'image',
            'recipe_name',
            'servings',
            'reference_url',
            'memo',
            ]
        

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

    
class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["step_no", "instruction"]