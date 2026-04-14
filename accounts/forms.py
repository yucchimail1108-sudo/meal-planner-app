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
            raise forms.ValidationError('このメールアドレスは既に登録されています')
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
    
# メールアドレス変更フォーム
class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(
        label="新しいメールアドレス",
        required=True
    )

    def clean_new_email(self):
        new_email = self.cleaned_data["new_email"]

        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("このメールアドレスはすでに登録されています")

        return new_email
    
    
# パスワード変更フォーム
class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="現在のパスワード",
        widget=forms.PasswordInput,
        required=True
    )
    new_password1 = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput,
        required=True
    )
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        widget=forms.PasswordInput,
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]

        if not self.user.check_password(current_password):
            raise forms.ValidationError("現在のパスワードが正しくありません")

        return current_password

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("new_password1")
        pw2 = cleaned_data.get("new_password2")

        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("入力されたパスワードが一致しません")

        return cleaned_data
    
    
# パスワード再設定メールアドレス入力フォーム
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="メールアドレス",
        required=True
    )

    def clean_email(self):
        email = self.cleaned_data["email"]

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは登録されていません")

        return email