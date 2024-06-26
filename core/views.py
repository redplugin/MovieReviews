import requests

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .forms import ReviewForm, CommentForm

from .models import Genre, Director, Movie, Review, Comment


def index(request):
    # Get all movies from the database
    movies = Movie.objects.annotate(num_reviews=Count('reviews'))

    # if director is specified:
    director_id = request.GET.get('director_id')
    director = None
    if director_id:
        director = Director.objects.get(pk=director_id)
        movies = movies.filter(directors=director)

    # if genre is specified:
    genre_id = request.GET.get('genre_id')
    genre = None
    if genre_id:
        genre = Genre.objects.get(pk=genre_id)
        movies = movies.filter(genres=genre)

    # if sorting parameters
    sort_by = request.GET.get('sort_by', 'title')
    if sort_by not in ['title', '-title', 'release_year', '-release_year', 'num_reviews', '-num_reviews']:
        sort_by = 'title'

    # Sort movies based on parameters
    movies = movies.order_by(sort_by)

    context = {
        'movies': movies,
        'sort_by': sort_by,
        'director': director,
        'genre': genre,
    }
    return render(request, 'core/index.html', context)


def movie_search(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            # Perform search based on the query
            movies = Movie.objects.filter(title__icontains=query)
            directors = Director.objects.filter(name__icontains=query)
            genres = Genre.objects.filter(name__icontains=query)
            if len(movies) > 0 or len(directors) > 0 or len(genres) > 0:
                message = f"Search results by your \"{query}\" query"
            else:
                message = f"No search results by your \"{query}\" query"
            return render(request, 'core/index.html', {
                'message': message,
                'movies': movies,
                'directors': directors,
                'genres': genres,
                'query': query,
            })
    # If no query or if method is not GET, render the index page without search results
    return render(request, 'core/index.html')


def movie_details(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    user = request.user  # If the user is authenticated
    if user.is_authenticated:
        user_reviews = Review.objects.filter(user=user)
        reviewed_movies = [review.movie_id for review in user_reviews]  # ids of movies that been reviewed by the user
    else:
        reviewed_movies = []

    # request to the OMDB API to get JSON with movie details
    omdb_api_key = 'a98a1cf1'  # my API KEY
    omdb_url = f'https://www.omdbapi.com/?i={movie.imdb_id}&apikey={omdb_api_key}'
    response = requests.get(omdb_url)
    if response.status_code == 200:
        movie_details = response.json()
        poster_url = movie_details.get('Poster', '')  # Get the poster URL from the response
    else:
        poster_url = ''

    return render(request, "core/movie.html", {
        "movie": movie,
        'reviewed_movies': reviewed_movies,
        'poster_url': poster_url,
    })


def review_details(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    is_user_the_author = review.user == request.user  # bool, which tells the current user the review's author

    # add comment to this review
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.review = review  # Link the comment to the review
            comment.save()
            messages.success(request, 'Your comment has been added successfully.')
            return redirect('review', review_id=review_id)
    else:
        form = CommentForm()

    return render(request, "core/review.html", {
        "form": form,
        "review": review,
        'is_user_the_author': is_user_the_author,
    })


@login_required
def toggle_like(request, review_id):
    review = Review.objects.get(pk=review_id)

    if review.likes.filter(id=request.user.id).exists():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)

    return redirect(request.META.get('HTTP_REFERER'))


# handle request made by new review form
@login_required
def write_review(request, movie_id):
    if not request.user.is_authenticated:
        # Redirect non-authenticated users to the login page
        return redirect('login')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie_id = movie_id
            review.save()
            return redirect('review', review_id=review.pk)
    else:
        form = ReviewForm()

    return render(request, 'core/write_review.html', {
        'form': form,
        'movie': Movie.objects.get(pk=movie_id)
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if request.method == 'GET':
        form = ReviewForm(instance=review)
        return render(request, 'core/edit_review.html', {'form': form, 'review': review})

    elif request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review', review_id=review.pk)
        else:
            # Render the form again if the form is not valid
            return render(request, 'core/edit_review.html', {'form': form, 'review': review})

    # Return a bad request response for unsupported methods
    return HttpResponseBadRequest("Unsupported HTTP method")


@login_required
def remove_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    # Check if the authenticated user is the author of the review
    if request.user == review.user:
        # If it's a POST request, delete the review
        if request.method == 'POST':
            review.delete()
            messages.success(request, 'Review deleted successfully.')  # Success message
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # Render the movie template with the review information
            return render(request, 'core/movie.html', {'review': review})
    else:
        # If the user is not the author, show an error message in the movie template
        messages.error(request, 'You are not the author of this review.')
        return redirect('movie', movie_id=review.movie.pk)


@login_required
def remove_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    review_id = comment.review.id
    if request.user == comment.user:
        if request.method == 'POST':
            comment.delete()
            messages.success(request, 'Comment deleted successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return render(request, 'core/review.html', {'comment': comment})
    else:
        messages.error(request, 'You are not the author of this comment.')
        return redirect('review', review_id=review_id)


@login_required
def user_page(request):
    user_reviews = Review.objects.filter(user=request.user)
    user_comments = Comment.objects.filter(user=request.user)

    return render(request, 'core/user_page.html', {
        'reviews': user_reviews,
        'comments': user_comments
    })




