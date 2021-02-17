from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = ("-пусто-")


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description",)
    search_fields = ("description",)
    list_filter = ("title",)
    empty_value_display = ("-пусто-")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "text", "active")
    list_filter = ("created",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
