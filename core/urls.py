from django.urls import path
from . import views

urlpatterns = [
     path("", views.index, name="index"),  # list of movies
     path("movie/<int:movie_id>", views.movie_details, name="movie"),  # movie details and its reviews

     path('review/<int:review_id>', views.review_details, name='review'),  # review details
     path('toggle-like/<int:review_id>/', views.toggle_like, name='toggle_like'),  # toggle like to reviews
     path('write-review/<int:movie_id>/', views.write_review, name='write_review'),
     path('edit-review/<int:review_id>/', views.edit_review, name='edit_review'),
     path('remove-review/<int:review_id>/', views.remove_review, name='remove_review'),


     path('remove-comment/<int:comment_id>/', views.remove_comment, name='remove_comment'),  # remove comment

     path('user_page', views.user_page, name='user_page'),
     path('movie-search/', views.movie_search, name='movie_search'),
]
