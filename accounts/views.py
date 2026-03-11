from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm,LoginForm


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
                return redirect('/')
            else:
                form.add_error(None, 'メールアドレスまたはパスワードが正しくありません。')
    else:
        form = LoginForm()
        
    return render(request, 'accounts/login.html', {'form': form}) 

def top_view(request):
    return render(request, 'top.html')      