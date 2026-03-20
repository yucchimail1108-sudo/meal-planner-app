from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm, NicknameChangeForm
from django.contrib import messages


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
        
    return  render(request, 'accounts/signup.html', {'form': form})

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
                form.add_error(None, 'メールアドレスまたはパスワードが正しくありません。')
    else:
        form = LoginForm()
        
    return render(request, 'accounts/login.html', {'form': form}) 

def top_view(request):
    return render(request, 'top.html') 

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        
    return redirect('top')

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
            messages.success(request, "ニックネームを変更しました。")
            return redirect("accounts:mypage")
    else:
        form = NicknameChangeForm(
            initial={
                "first_name": request.user.first_name
            }
        )

    return render(
        request,
        "accounts/nickname_change.html",
        {
            "form": form,
            "current_nickname": request.user.first_name,          
        }
    )