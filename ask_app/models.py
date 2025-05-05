import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


# Create a Post Model
class Post(models.Model):
    # The user who made the post
    user = models.ForeignKey(User, related_name="posts", on_delete=models.DO_NOTHING)
    # Title text of the post
    title = models.CharField(max_length=80)
    # Body text of the post
    body = models.CharField(max_length=5000)
    # Date post was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} " f"({self.created_at:%Y-%m-%d %H:%M})" f"{self.body}..."


# Create a User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )
    date_modified = models.DateTimeField(User, auto_now=True)

    def __str__(self):
        return self.user.username


# Create a Profile when new user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        # Have the user follow themselves
        user_profile.follows.set([instance.profile.id])


post_save.connect(create_profile, sender=User)


class Comment(models.Model):
    id = models.CharField(
        max_length=100,
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    parent_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    body = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        try:
            return f"{self.author.username} : {self.body[:30]}"
        except:
            return f"no author : {self.body[:30]}"

    def is_root(self):
        return self.parent is None

    def get_root_post_id(self):
        return (
            self.parent_post.id if self.parent_post else self.parent.get_root_post_id()
        )
