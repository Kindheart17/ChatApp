from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from Chat.models import Profile
from .forms import SignupForm
from .forms import EditProfileForm


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("chat:emptyChat"))

    return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def login_user(request):
    errors = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            errors = "Incorrect Login Details."

    return render(
        request,
        "users/login.html",
        {
            "errors": errors,
        },
    )


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
    else:
        form = SignupForm()

    return render(request, "users/signup.html", {"form": form})


@csrf_exempt
def editProfile(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first = request.POST.get("first")
        last = request.POST.get("last")
        email = request.POST.get("email")
        password = request.POST.get("password")
        image = request.FILES.get("image")
        if image:
            request.user.profile.image = image
            request.user.profile.save()
            request.user.save()
            return redirect("profile")
        if password == "********":
            request.user.username = username
            request.user.first_name = first
            request.user.last_name = last
            request.user.email = email
            request.user.save()
            return redirect("profile")
        else:
            request.user.username = username
            request.user.first_name = first
            request.user.last_name = last
            request.user.email = email
            request.user.password = password
            request.user.save()
            login(request, request.user)
            return redirect("profile")

    return render(request, "users/edit.html")


def profile(request):
    return render(request, "users/profile.html")


def image(request):
    return render(request, "users/image.html")
