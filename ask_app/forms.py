from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post, Profile


class PostForm(forms.ModelForm):
    # title = forms.CharField(
    #     required=True,
    #     widget=forms.widgets.Textarea(
    #         attrs={"placeholder": "Title", "class": "form-control", "rows": "1"}
    #     ),
    #     label="",
    # )
    # body = forms.CharField(
    #     required=True,
    #     widget=forms.widgets.Textarea(
    #         attrs={"placeholder": "What is your question?", "class": "form-control"}
    #     ),
    #     label="",
    # )

    class Meta:
        model = Post
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Title"}),
            "body": forms.Textarea(attrs={"placeholder": "Ask a question!"})
        }
        exclude = ("user", "likes")

    # put a margin between the title and body
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("title", css_class="mb-3"),
            Field("body", css_class="mb-3"),
        )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        ),
    )
    first_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    # This provides error text when user provides invalid input
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["username"].label = ""
        self.fields["username"].help_text = (
            '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
        )

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password1"].label = ""
        self.fields["password1"].help_text = (
            "<ul class=\"form-text text-muted small\"><li>Your password can't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can't be a commonly used password.</li><li>Your password can't be entirely numeric.</li></ul>"
        )

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"
        self.fields["password2"].label = ""
        self.fields["password2"].help_text = (
            '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
        )


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.TextInput(attrs={"placeholder": "Add comment..."})}
        labels = {"body": ""}


class ProfileSettingsForm(forms.ModelForm):
    picture = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={"accept": "image/*", "class": "form-control"}),
        label="Profile Picture",
    )
    username = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"class": "form-control"}),
        label="Username",
    )
    bio = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"class": "form-control"}),
        label="Bio",
    )
    dark_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Color Theme",
    )

    class Meta:
        model = Profile
        fields = [
            "picture",
            "bio",
            "dark_mode",
        ]  # Removed 'username' because it's part of the User model
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["username"].widget.attrs[
                "placeholder"
            ] = self.instance.user.username
            self.fields["bio"].widget.attrs["placeholder"] = self.instance.bio
            self.fields["picture"].widget.attrs["placeholder"] = self.instance.picture
            self.fields["dark_mode"].widget.attrs["placeholder"] = str(
                self.instance.dark_mode
            )
