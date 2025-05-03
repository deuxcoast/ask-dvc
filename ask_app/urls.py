from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile_list/", views.profile_list, name="profile_list"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.signup_user, name="signup"),
    path("post/", views.post, name="post"),
    path("post/<pk>", views.post_page, name="post_page"),
    path("comment/sent/<pk>", views.comment_sent, name="comment_sent"),
    path("comment/delete/<pk>", views.comment_delete, name="comment_delete"),
    path("reply/sent/<pk>", views.reply_sent, name="reply_sent"),
]
