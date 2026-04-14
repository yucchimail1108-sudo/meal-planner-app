from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import PasswordResetRequestForm

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("mypage/", views.mypage_view, name="mypage"),
    path("nickname/change/", views.nickname_change_view, name="nickname_change"),
    path("email/change/", views.email_change_view, name="email_change"),
    path("password/change/", views.password_change_view, name="password_change"),
    
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            form_class=PasswordResetRequestForm,
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
