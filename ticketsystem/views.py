import json

from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from datetime import datetime, timezone
import datetime

from django.contrib.auth.decorators import login_required

#TODO: For testing only
from django.views.decorators.csrf import csrf_exempt

from .models import User, Ticket


# Helper Functions
# Returns number of days
def calc_age(date):
    now = datetime.datetime.now(timezone.utc)
    delta = now - date
    return delta.days if delta.days else 0


def index(request):
    return render(request, "index.html")


def my_tickets(request):
    pass


def my_dashboard(request):
    pass


def profile(request, username):
    pass


def ticket(request, id):

    user = request.user
    if user.is_anonymous:
        # TODO: Notification
        return HttpResponseRedirect(reverse('index'))

    ticket_to_display = Ticket.objects.all().get(id=id)
    if not ticket_to_display:
        return render(request, "ticket.html", {
            'message': 'This ticket does not exist!',
            'ticket': '',
        })
    age = calc_age(ticket_to_display.timestamp)
    return render(request, "ticket.html", {
        'message': '',
        'ticket': ticket_to_display,
        'age': age,
    })


def get_all_tickets(request):
    tickets = Ticket.objects.all()

    ages = []
    for elem in tickets:
        ages.append(calc_age(elem.timestamp))
    tickets = tickets.order_by('-timestamp').all()
    return JsonResponse({'tickets': [ticket_.serialize() for ticket_ in tickets], 'age': ages}, safe=False)


# TODO: Nicht SPA redirect ersetzen durch js verhalten
# TODO: Remove age + ticket if not needed
@csrf_exempt
@login_required
def new_ticket(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('index'))

    user = request.user
    if user.is_anonymous:
        #TODO: Notification
        return HttpResponseRedirect(reverse('index'))

    data = json.loads(request.body)

    newticket = Ticket()
    newticket.owner = user
    newticket.content = data.get('content')
    newticket.status = 'New'
    newticket.save()
    age = calc_age(newticket.timestamp)

    return JsonResponse({
        "message": "Ticket created successfully.",
        'ticket': newticket.serialize(),
        'age': age,
    },  safe=False)


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
