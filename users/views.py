from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User


def login_view(request):
    message = None
    stored_messages = messages.get_messages(request)
    for msg in stored_messages:
        message = msg  # Retrieve the last message from the session

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # return HttpResponseRedirect(reverse("index"))
            return HttpResponseRedirect(reverse("user_page"))
        else:
            return render(request, "users/login.html", {
                "message": "Invalid credentials."
            })

    return render(request, "users/login.html", {
        "message": message,
    })


def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {
        "message": "Logged out."
    })


def register(request):
    message = None

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            message = f"Account created for {username}. You can now log in."
            messages.success(request, message)
            return redirect('login')
        else:
            # the last error message
            message = list(form.errors.values())[-1][-1]
            messages.error(request, message)
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form, 'message': message})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("user_page"))
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/update_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            # Update the user's session to reflect the new password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse("user_page"))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


@login_required
def delete_user(request):
    if request.method == 'POST':
        # Delete the user account
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('index')
    return render(request, 'users/delete_user.html')
