from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.utils.ipv6 import ValidationError


def user_profile_pic_path(instance, filename):
    username = instance.username
    return f"{username}/profile_pic/{filename}"


def user_post_image_path(instance, filename):
    username = instance.user.username
    return f"{username}/post/{filename}"


class User(AbstractUser):
    karma = models.IntegerField(default=1)
    profile_pic = models.ImageField(
        upload_to=user_profile_pic_path, blank=True, null=True
    )
    account_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Tag(models.Model):
    objects: models.Manager = models.Manager()
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"tag: {self.name}"


class CommunityType(models.Model):
    objects: models.Manager = models.Manager()
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"Community_type: {self.name}"


class Community(models.Model):
    objects: models.Manager = models.Manager()
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=3000)
    community_created = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(Tag, related_name="communities")

    community_type = models.ForeignKey(
        CommunityType, on_delete=models.PROTECT, related_name="communities"
    )

    def __str__(self):
        return f"r/{self.name}"


class Post(models.Model):
    objects: models.Manager = models.Manager()
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=5000, null=True, blank=True)
    url = models.CharField(max_length=2000, null=True, blank=True)
    image_post = models.ImageField(
        upload_to=user_post_image_path, blank=True, null=True
    )

    vote_score = models.IntegerField(default=1)  # pyright: ignore
    tags = models.JSONField(default=list, blank=True, null=True)

    post_created = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="submitted_posts"
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="posts"
    )

    def __str__(self):
        return f"{self.title} in r/{self.community.name}"


class Comment(models.Model):
    objects: models.Manager = models.Manager()
    text = models.CharField(max_length=5000)
    comment_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
    )

    def __str__(self):
        return f"Comment on post '{self.post.title[:20]}...' by {self.user.username}"


class Vote(models.Model):
    objects: models.Manager = models.Manager()
    direction = models.SmallIntegerField(default=1)  # pyright: ignore

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="votes",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="votes",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "post"],
                name="unique_post_vote",
                condition=Q(post__isnull=False),
            ),
            UniqueConstraint(
                fields=["user", "comment"],
                name="unique_comment_vote",
                condition=Q(comment__isnull=False),
            ),
            CheckConstraint(
                check=Q(direction__in=[1, -1]),
                name="direction_is_like_or_dislike",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.comment and self.post:
            raise ValidationError("It should be either comment or post")

        target_model = Post if self.post else Comment
        target_obj = self.post if self.post else self.comment

        if not target_obj:
            raise ValidationError(
                "A vote must be associated with either post or comment"
            )

        querySet = Vote.objects.filter(
            user=self.user,
            **({"post": self.post} if self.post else {"comment": self.comment}),
        )

        if querySet.exists():
            existing_vote = querySet.first()

            if existing_vote.direction == self.direction:
                target_model.objects.filter(pk=target_obj.id).update(
                    vote_score=F("vote_score") - self.direction
                )
                existing_vote.delete()
                return
            else:
                diff = self.direction * 2
                target_model.objects.filter(pk=target_obj.id).update(
                    vote_score=F("vote_score") + diff
                )
                existing_vote.direction = self.direction
                Vote.objects.filter(pk=existing_vote.pk).update(
                    direction=self.direction
                )
                return

        target_model.objects.filter(pk=target_obj.id).update(
            vote_score=F("vote_score") + self.direction
        )
        super().save(*args, **kwargs)

    def __str__(self):
        voted_on = self.post.title if self.post else f"Comment ID {self.comment.id}"
        action = "Upvoted" if self.direction == 1 else "Downvoted"
        return f"{self.user.username} {action} on {voted_on}"
