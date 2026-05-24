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

from finance.views import (
    register_view,
    login_view,
    dashboard,
    logout_view,
    home_view,
    add_income,
    view_income,
    add_expense,
    view_expenses,
    set_goal
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('register/', register_view),

    path('login/', login_view),

    path('dashboard/', dashboard),

    path('logout/', logout_view),
    
    path('', home_view),
    
    path('add-income/',add_income),
    
    path('view-income/',view_income),

    path('add-expense/',add_expense),
    
    path('view-expenses/',view_expenses),
    
    path('set-goal/',set_goal),

]
