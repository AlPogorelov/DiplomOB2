from django.contrib import admin
from content.models import Category, Content, Media


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sub_price', 'category', 'body_text', 'published')
    list_filter = ('category',)
    search_fields = ('name', )


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'file', )
    list_filter = ('content',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name', )
