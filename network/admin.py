from django.contrib import admin

from .models import Comment, Community, CommunityType, Post, Tag, User, Vote

# Register your models here.

admin.site.register(User)
admin.site.register(Community)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Tag)
admin.site.register(CommunityType)
