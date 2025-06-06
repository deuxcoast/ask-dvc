from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import Comment, LikedPost, Post, Profile

# Register your models here.
admin.site.unregister(Group)


# Make profile information part of user information
class ProfileInline(admin.StackedInline):
    model = Profile


# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    # display username fields on admin page
    fields = ["username", "email"]
    inlines = [ProfileInline]


# Unregister Initial User
admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(LikedPost)
