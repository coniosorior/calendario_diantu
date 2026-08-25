"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from apps.accounts.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/login/', LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('cuentas/logout/', LogoutView.as_view(), name='logout'),
    path('cuentas/password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('cuentas/password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('cuentas/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('cuentas/password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('cuentas/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('cuentas/reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('cuentas/', include('apps.accounts.urls')),
    path('categorias/', include('apps.categories.urls')),
]
