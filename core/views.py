from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .forms import ReviewForm, CommentForm

from .models import Genre, Movie, Review, Comment


def index(request):
    # Get all movies from the database
    movies = Movie.objects.all()

    # Sorting parameters
    sort_by = request.GET.get('sort_by', 'title')
    if sort_by not in ['title', '-title', 'release_year', '-release_year', 'reviews', '-reviews']:
        sort_by = 'title'

    # Sort movies based on parameters
    movies = movies.order_by(sort_by)

    context = {
        'movies': movies,
        'sort_by': sort_by,
    }

    return render(request, 'core/index.html', context)


def movie_search(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            # Perform search based on the query
            movies = Movie.objects.filter(title__icontains=query)
            if len(movies) > 0:
                message = f"Search results by your \"{query}\" query"
            else:
                message = f"No search results by your \"{query}\" query"
            return render(request, 'core/index.html', {
                'message': message,
                'movies': movies,
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

    return render(request, "core/movie.html", {
        "movie": movie,
        'reviewed_movies': reviewed_movies,
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
        # Redirect non-authenticated users to the login page or display a message
        return redirect('login')  # Assuming you have a 'login' URL name

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
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # Render the movie template with the review information
            return render(request, 'core/movie.html', {'review': review})
    else:
        # If the user is not the author, show an error message in the movie template
        messages.error(request, 'You are not the author of this review.')  # Error message
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




