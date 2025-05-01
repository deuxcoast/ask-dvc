from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render

from .forms import PostForm, SignUpForm
from .models import Post, Profile


def index(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, "Your post was successful.")
                return redirect("index")

        posts = Post.objects.all().order_by("-created_at")
        return render(request, "index.html", {"posts": posts, "form": form})

    else:
        posts = Post.objects.all().order_by("-created_at")
        return render(request, "index.html", {"posts": posts})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, "profile_list.html", {"profiles": profiles})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect("index")


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        posts = Post.objects.filter(user_id=pk)

        # Post form logic
        if request.method == "POST":
            # Get current user
            current_user_profile = request.user.profile
            # Get form data
            action = request.POST["follow"]
            # Decide to follow or unfollow
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)

            # Save the profile
            current_user_profile.save()

        return render(request, "profile.html", {"profile": profile, "posts": posts})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect("index")


def login_user(request):
    # if the request method is POST, then handle the form submission, otherwise
    # send the user to the login page
    if request.method == "POST":
        # Assign username and password from form submission to variables
        username = request.POST["username"]
        password = request.POST["password"]

        # use the above credentials to login. If the credentials match an existing
        # user than a user object will be returned
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You have succesfully logged in."))
            return redirect("index")
        else:
            messages.error(request, ("There was an error logging in."))
            return redirect("login")
    else:
        return render(request, "login.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out."))
    return redirect("index")


def signup_user(request):
    # Get the form model
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            # first_name = form.cleaned_data["first_name"]
            # last_name = form.cleaned_data["last_name"]
            # email = form.cleaned_data["email"]

            # Login the user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have been logged in.")
            return redirect("index")

    return render(request, "sign_up.html", {"form": form})

def profile_settings(request, pk):
    return render(request, 'settings.html', {})
