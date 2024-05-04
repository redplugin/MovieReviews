from django.urls import path
from . import views

urlpatterns = [
     path("login", views.login_view, name="login"),
     path("logout", views.logout_view, name="logout"),
     path('register', views.register, name='register'),
     path('update_profile', views.update_profile, name='update_profile'),
     path('change_password', views.change_password, name='change_password'),
     path('delete_user', views.delete_user, name='delete_user'),
]
