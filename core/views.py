from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .forms import ReviewForm

from .models import Genre, Movie, Review, Comment


def index(request):
    # Query to get all movies ordered by the count of reviews in descending order
    try:
        movies = Movie.objects.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')
    except Movie.DoesNotExist:
        movies = []

    user = request.user  # If the user is authenticated
    user_reviews = Review.objects.filter(user=user)
    reviewed_movies = [review.movie_id for review in user_reviews]  # ids of movies that been reviewed by the user

    return render(request, "core/index.html", {
        'movies': movies,
        'reviewed_movies': reviewed_movies,  # movies reviewed by this user
    })


def movie(request, movie_id):

    movie_details = get_object_or_404(Movie, pk=movie_id)

    user = request.user  # If the user is authenticated
    user_reviews = Review.objects.filter(user=user)
    reviewed_movies = [review.movie_id for review in user_reviews]  # ids of movies that been reviewed by the user

    return render(request, "core/movie.html", {
        "movie": movie_details,
        'reviewed_movies': reviewed_movies,
    })


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
        # Redirect non-authenticated users to the login page or display a message
        return redirect('login')  # Assuming you have a 'login' URL name

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie_id = movie_id
            review.save()
            return redirect('movie', movie_id=movie_id)
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
            return redirect('movie', movie_id=review.movie.pk)
        else:
            # Render the form again with error messages
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
            return redirect('movie', movie_id=review.movie.pk)
        else:
            # Render the movie template with the review information
            return render(request, 'core/movie.html', {'review': review})
    else:
        # If the user is not the author, show an error message in the movie template
        messages.error(request, 'You are not the author of this review.')  # Error message
        return redirect('movie', movie_id=review.movie.pk)
