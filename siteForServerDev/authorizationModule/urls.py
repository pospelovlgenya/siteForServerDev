"""
URL configuration for siteForServerDev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name="signUp"),
    path('signin', views.signin, name="signIn"),
    path('signout', views.signout, name='signOut'),
    path('refresh', views.refreshtoken, name='refreshToken'),
    path('f2a', views.f2a_check, name="f2a"),
    path('toomany', views.too_many, name="tooMany"),
    path('delete/<str:token_spec>/', views.delete_token),
]
