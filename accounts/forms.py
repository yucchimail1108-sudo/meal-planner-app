from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    nickname = forms.CharField(label='ニックネーム', max_length=150, required=True)
    email = forms.EmailField(label='メールアドレス',required=True)
    
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='パスワード再入力',
        widget=forms.PasswordInput
    )
    
    class Meta:
        model = User
        fields = ('nickname', 'email', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています。')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        nickname = self.cleaned_data['nickname']
        
        user.username = email
        user.email = email
        user.first_name = nickname
        
        if commit:
            user.save()
        return user
    

class LoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス', required=True)
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput,
        required=True
    )
    
# ニックネーム変更フォーム
class NicknameChangeForm(forms.Form):
    new_first_name = forms.CharField(
        max_length=64,
        label="新しいニックネーム"
    )