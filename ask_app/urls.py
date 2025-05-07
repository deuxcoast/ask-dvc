from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile_list/", views.profile_list, name="profile_list"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.signup_user, name="signup"),
    path("profile/<int:pk>/settings", views.profile_settings, name="profile_settings"),
    path(
        "profile/<int:pk>/settings/edit",
        views.edit_profile_settings,
        name="edit_settings",
    ),
    path("post/", views.create_post, name="post"),
    path("post/<pk>", views.post_page, name="post_page"),
    path("post/<pk>/like/", views.like_post, name="like_post"),
    path("comment/<pk>/like/", views.like_comment, name="like_comment"),
    path("comment/sent/<pk>", views.comment_sent, name="comment_sent"),
    path("comment/delete/<pk>", views.comment_delete, name="comment_delete"),
    path("reply/sent/<pk>", views.reply_sent, name="reply_sent"),
    path("search/", views.search, name="search"),
    path("toggle-dark-mode/", views.toggle_theme, name="toggle_theme"),
]
