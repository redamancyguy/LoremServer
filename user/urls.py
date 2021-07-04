from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path(r'login', views.Login.as_view(), name='login'),
    path(r'logout', views.Logout.as_view(), name='logout'),
    path(r'register', views.Register.as_view(), name='register'),
    path(r'getcaptcha', views.getCaptcha, name='getCaptcha'),
    path(r'changepw', views.ChangePassword.as_view(), name='changePD'),
    path(r'userinfo', views.UserInfo.as_view(), name='userinfo'),
]
