from django.contrib import admin
from .models import Genre, Movie, Review, Comment


# Register your models here.
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "release_year")


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "text", "rating")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "review", "text")


admin.site.register(Genre, GenreAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
