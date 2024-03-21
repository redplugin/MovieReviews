from django.urls import path
from . import views

urlpatterns = [
     path("", views.index, name="index"),  # list of movies
     path("movie/<int:movie_id>", views.movie, name="movie"),  # movie details and reviews
     path('toggle-like/<int:review_id>/', views.toggle_like, name='toggle_like'),  # toggle like to reviews
     path('write-review/<int:movie_id>/', views.write_review, name='write_review'),
     path('edit-review/<int:review_id>/', views.edit_review, name='edit_review'),
     path('remove-review/<int:review_id>/', views.remove_review, name='remove_review'),
]
