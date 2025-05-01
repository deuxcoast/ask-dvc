from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile_list/", views.profile_list, name="profile_list"),
    path("profile/<int:pk>", views.profile, name="profile"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.signup_user, name="signup"),
    path("profile/<int:pk>/settings", views.profile_settings, name="profile_settings"),
    path("post/", views.post, name="post"),
]
