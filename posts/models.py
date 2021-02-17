from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL, related_name="posts")
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост с комментарием",
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
    )
    created = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        comment_text = self.text[:20]
        comment_pub_date = self.created
        return f'Комментарий {comment_text}... от {comment_pub_date:%d.%m.%Y}.'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'
