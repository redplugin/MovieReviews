from django.contrib import admin
from .models import Genre, Director, Movie, Review, Comment


# Register your models here.
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class DirectorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bio", "latitude", "longitude")


class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "release_year")


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "text", "rating")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "review", "text")


admin.site.register(Genre, GenreAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
