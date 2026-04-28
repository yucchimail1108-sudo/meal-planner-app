from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm, NicknameChangeForm, EmailChangeForm, PasswordChangeForm
from django.contrib import messages
from apps.recipes.initial_recipe_service import create_initial_recipes_for_user

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_initial_recipes_for_user(user)
            login(request, user)
            return redirect('app_home')
    else:
        form = SignUpForm()
        
    return render(request, "accounts/signup.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'メールアドレスまたはパスワードが正しくありません')
    else:
        form = LoginForm()
        
    return render(request, 'accounts/login.html', {'form': form}) 

def top_view(request):
    return render(request, 'portfolio.html') 

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        
    return redirect('home')

# マイページ画面
@login_required
def mypage_view(request):
    context = {}

    return render(
        request,
        "accounts/mypage.html",
        context
    )
    
# ニックネーム変更画面
@login_required
def nickname_change_view(request):
    if request.method == "POST":
        form = NicknameChangeForm(request.POST)

        if form.is_valid():
            request.user.first_name = form.cleaned_data["new_first_name"]
            request.user.save()
            messages.success(request, "ニックネームを変更しました")
            return redirect("accounts:mypage")
    else:
        form = NicknameChangeForm()

    return render(
        request,
        "accounts/nickname_change.html",
        {
            "form": form,
            "current_nickname": request.user.first_name,          


        }
    )
    
# メールアドレス変更画面
@login_required
def email_change_view(request):
    if request.method == "POST":
        form = EmailChangeForm(request.POST)

        if form.is_valid():
            new_email = form.cleaned_data["new_email"]

            request.user.email = new_email
            request.user.username = new_email  # ログイン用も更新
            request.user.save()

            messages.success(request, "メールアドレスを変更しました")
            return redirect("accounts:mypage")
    else:
        form = EmailChangeForm()

    return render(
        request,
        "accounts/email_change.html",
        {
            "form": form,
            "current_email": request.user.email,
        }
    )
    
# パスワード変更画面
@login_required
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            request.user.set_password(new_password)
            request.user.save()
            
            update_session_auth_hash(request, request.user)

            messages.success(request, "パスワードを変更しました")
            return redirect("accounts:mypage")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "accounts/password_change.html",
        {"form": form}
    )
    
