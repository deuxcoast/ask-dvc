from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CommentCreateForm, PostForm, ProfileSettingsForm
from .models import Category, Comment, Post, PostCategory, Profile


# displays all posts on index (home) page
def index(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None)
        selected_category = request.GET.get("category", "all")
        categories = Category.objects.all()

        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()

                messages.success(request, "Your post was successful.")
                return redirect("index")

        if selected_category == "all":
            posts = Post.objects.annotate(comment_count=Count("comments")).order_by(
                "-created_at"
            )

        else:
            posts = (
                Post.objects.filter(categories__name__iexact=selected_category)
                .annotate(comment_count=Count("comments"))
                .order_by("-created_at")
            )

        page_number = request.GET.get("page", 1)
        paginator = Paginator(posts, 50)
        page_obj = paginator.get_page(page_number)

        return render(
            request, "index.html", {"posts": page_obj, "categories": categories}
        )

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


def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out."))
    return redirect("index")


def post(request):
    # if the user is logged in, allow them to post
    if request.user.is_authenticated:
        form = PostForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()

                selected_categories = request.POST.getlist("categories")
                # for each category name, checks if it exists
                # if it exists, return, otherwise create and return
                for category_name in selected_categories:
                    category, created = Category.objects.get_or_create(
                        name=category_name
                    )
                    PostCategory.objects.create(post=post, category=category)

                messages.success(request, "Your post was successful.")
                return redirect("index")

        posts = Post.objects.all().order_by("-created_at")
        categories = Category.objects.all()

        return render(
            request,
            "post.html",
            {"posts": posts, "form": form, "categories": categories},
        )


def create_post(request):
    if not request.user.is_authenticated:
        return redirect("login")  # or show message

    form = PostForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Your post was successful.")
            return redirect("index")
        else:
            print(form.errors)  # Debug invalid form

    posts = Post.objects.all().order_by("-created_at")
    return render(request, "post.html", {"form": form, "posts": posts})


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


# TODO: implement this differently, a user shouldn't have to be logged in to use
# dark mode.
@login_required
def toggle_theme(request):
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    print(profile.dark_mode)
    theme = "dark" if profile.dark_mode else "light"
    return HttpResponse(
        f'document.documentElement.setAttribute("data-bs-theme", "{theme}");',
        content_type="application/javascript",
    )
