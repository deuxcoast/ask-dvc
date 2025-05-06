from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CommentCreateForm, PostForm, SignUpForm
from .models import Comment, Post, Profile


# displays all posts on index (home) page
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

        posts = Post.objects.annotate(comment_count=Count("comments")).order_by(
            "-created_at"
        )
        page_number = request.GET.get("page", 1)
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page_number)

        return render(request, "index.html", {"posts": page_obj})

    else:
        posts = Post.objects.annotate(comment_count=Count("comments")).order_by(
            "-created_at"
        )
        return render(request, "index.html", {"posts": posts})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, "profile_list.html", {"profiles": profiles})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect("index")


def profile(request, username):
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)

        follows = profile.follows.exclude(user=profile.user)
        followed_by = profile.followed_by.exclude(user=profile.user)

        posts = user.posts.all()
        # posts = Post.objects.filter(user=user)

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

        return render(
            request,
            "profile.html",
            {
                "profile": profile,
                "posts": posts,
                "follows": follows,
                "followed_by": followed_by,
            },
        )
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


def post(request):
    # if the user is logged in, allow them to post
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
        return render(request, "post.html", {"posts": posts, "form": form})


def post_page(request, pk):
    post = get_object_or_404(
        Post.objects.annotate(comment_count=Count("comments")), id=pk
    )

    comment_form = CommentCreateForm()
    top_level_comments = post.comments.filter(parent__isnull=True).order_by(
        "-created_at"
    )

    context = {
        "post": post,
        "comment_form": comment_form,
        "reply_form": comment_form,
        "comments": top_level_comments,
        "comment_count": post.comment_count,
    }
    return render(request, "post_page.html", context)


def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    user_exists = post.likes.filter(id=request.user.id).exists()

    if user_exists:
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    # Get the referring URL
    referer = request.META.get("HTTP_REFERER")

    # Validate the referer is safe to redirect to
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}
    ):
        return HttpResponseRedirect(referer)

    # Fallback to the post page
    return redirect("post_page", post.id)


@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)

    if request.method == "POST":
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            # comment.root_post = post
            comment.save()

    return redirect("post_page", post.id)

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    if request.method == "POST":
        post_id = comment.get_root_post_id()
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect("post_page", post_id)

    return render(request, "comment_delete.html", {"comment": comment})


@login_required
def reply_sent(request, pk):
    parent_comment = get_object_or_404(Comment, id=pk)

    if request.method == "POST":
        form = CommentCreateForm(request.POST)  # use the same form as for comments
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent = parent_comment
            reply.parent_post = parent_comment.parent_post  # inherit post
            reply.save()

    return redirect("post_page", parent_comment.parent_post.id)


def like_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    user_exists = comment.likes.filter(id=request.user.id).exists()

    if user_exists:
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return redirect("post_page", comment.parent_post.id)


def search(request):
    if request.method == "POST":

        # Get input from the search form
        search_term = request.POST["search"]

        # Search database for posts matching the search term
        # We use the Q object to allow us to search across both the title and
        # body columns.

        # This will eventually become a bottleneck. The two main solutions are
        # to switch to a more feature-full db like Postgres that allows full-text
        # search, or use a search-specific product like ElasticSearch
        post_results = Post.objects.filter(
            Q(title__icontains=search_term) | Q(body__icontains=search_term)
        )

        return render(
            request,
            "search_results.html",
            {"search_term": search_term, "post_results": post_results},
        )


def profile_settings(request, pk):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user_id=pk)

        # Pass the profile instance to the template
        return render(request, "settings.html", {"profile": profile})

    # Redirect to login page if user is not authenticated
    return redirect("login")


def edit_profile_settings(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = get_object_or_404(Profile, user_id=pk)

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user.username = form.cleaned_data["username"]
            profile.user.save()
            profile.save()

            # Force database reload to ensure latest data is displayed
            profile.refresh_from_db()

            print(
                "Updated Profile:", profile.bio, profile.picture, profile.dark_mode
            )  # Debugging confirmation

            return redirect("profile_settings", pk=pk)
        else:
            print("Form errors:", form.errors)  # Debugging

    else:
        form = ProfileSettingsForm(instance=profile)

    return render(request, "settings_edit.html", {"form": form, "profile": profile})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    if request.method == "POST":
        post_id = comment.get_root_post_id()
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect("post_page", post_id)

    return render(request, "comment_delete.html", {"comment": comment})


@login_required
def reply_sent(request, pk):
    parent_comment = get_object_or_404(Comment, id=pk)

    if request.method == "POST":
        form = CommentCreateForm(request.POST)  # use the same form as for comments
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent = parent_comment
            reply.parent_post = parent_comment.parent_post  # inherit post
            reply.save()

    return redirect("post_page", parent_comment.parent_post.id)


def like_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    user_exists = comment.likes.filter(id=request.user.id).exists()

    if user_exists:
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return redirect("post_page", comment.parent_post.id)


def search(request):
    if request.method == "POST":

        # Get input from the search form
        search_term = request.POST["search"]

        # Search database for posts matching the search term
        # We use the Q object to allow us to search across both the title and
        # body columns.

        # This will eventually become a bottleneck. The two main solutions are
        # to switch to a more feature-full db like Postgres that allows full-text
        # search, or use a search-specific product like ElasticSearch
        post_results = Post.objects.filter(
            Q(title__icontains=search_term) | Q(body__icontains=search_term)
        )

        return render(
            request,
            "search_results.html",
            {"search_term": search_term, "post_results": post_results},
        )
>>>>>>> main
