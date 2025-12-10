"""django_realestate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path

from django.contrib.auth import views as auth_views

from pages import views as page_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', page_views.landing_page, name='landing_page'),

    path('signin', page_views.login_page, name='login'),
    path('signup', page_views.signup_page, name='signup'),
    path('logout', page_views.logout_page, name='logout'),
    
    path('users/', include('users.urls')),
    path('properties/', include('properties.urls')),
    
    path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name='pages/password_reset.html'),
        name='reset_password'
    ),
    path('reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name='pages/password_reset_send.html'),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='pages/password_reset_form.html'),
        name='password_reset_confirm'
        ),
    path('reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='pages/password_reset_done.html'),
        name='password_reset_complete'
    ),
]
