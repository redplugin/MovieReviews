from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomUserCreationForm


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
