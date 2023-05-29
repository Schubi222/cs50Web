import json

from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from datetime import datetime, timezone
import datetime

#TODO: For testing only
from django.views.decorators.csrf import csrf_exempt

from .models import User, Ticket


def index(request):
    return render(request, "index.html")


def my_tickets(request):
    pass


def my_dashboard(request):
    pass


def profile(request, username):
    pass


def ticket(request, id):
    return render(request, "ticket.html")


def get_all_tickets(request):
    tickets = Ticket.objects.all()
    now = datetime.datetime.now(timezone.utc)
    ages = []
    for elem in tickets:
        delta = now - elem.timestamp
        ages.append(delta.days if delta.days else 0)
    return JsonResponse({'tickets': [ticket.serialize() for ticket in tickets], 'age': ages}, safe=False)


#TODO: Nicht SPA redirect ersetzen durch js verhalten
@csrf_exempt
def new_ticket(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('index'))

    user = request.user
    if user == user.is_anonymous:
        #TODO: Notification
        return HttpResponseRedirect(reverse('index'))

    data = json.loads(request.body)

    newticket = Ticket()
    newticket.owner = user
    newticket.content = data.get('content')
    newticket.status = 'New'
    newticket.save()

    return JsonResponse({"message": "Ticket created successfully."}, status=201)


# Login/Logout/Register copied from Assignment 4
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")
