from django.contrib import admin

from .models import Group, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'pub_date', 'author', 'group', 'text', 'image')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'author', 'post', 'text')
    search_fields = ('text',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
