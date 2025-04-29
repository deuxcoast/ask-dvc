from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import Post, Profile

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

# Reregister User
admin.site.register(User, UserAdmin)

# Register Post
admin.site.register(Post)
