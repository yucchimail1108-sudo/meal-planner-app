from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("mypage/", views.mypage_view, name="mypage"),
    path("nickname/change/", views.nickname_change_view, name="nickname_change"),
    path("email/change/", views.email_change_view, name="email_change"),
    path("password/change/", views.password_change_view, name="password_change"),
]
