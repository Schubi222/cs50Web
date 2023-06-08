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

from .models import User, Ticket, LogEntry

PERMISSION_DENIED_MESSAGE = "You do not have the permission to do that"

# Helper Functions
# Returns number of days
def calc_age(date):
    now = datetime.datetime.now(timezone.utc)
    delta = now - date
    return delta.days if delta.days else 0


# Everything but implying that something went wrong and the result should be returned
def form_standard_check(request, to_be_created):
    if request.method != 'POST':
        return JsonResponse({
            "message": f"Something went wrong while leaving a {to_be_created}!",
            'error': True
        })

    user = request.user
    if user.is_anonymous:
        # TODO: Notification
        return JsonResponse({
            "message": "You have to be logged in to do that!",
            'error': True
            })
    return None


# orders by -timestamp and calcs all ages
# returns tickets and ages
def prep_tickets(tickets):
    if not tickets:
        return None, None

    tickets = tickets.order_by('-timestamp').all()
    ages = []
    for ticket_ in tickets:
        ages.append(calc_age(ticket_.timestamp))

    return tickets, ages


def index(request):
    return render(request, "index.html")


def my_tickets(request):
    return render(request, "myticket.html")


def my_team(request):
    pass


def create_worker(request):
    pass


def change_permissions(request):
    pass


@login_required
def my_tickets_get(request):
    user = request.user
    user = User.objects.get(username=user)

    worker_tickets = None
    user_tickets = Ticket.objects.filter(owner=user).all()

    if user.permission == User.Permission.Lead_Worker or user.permission == User.Permission.Worker:
        worker_tickets = Ticket.objects.filter(assigned_to=user).all()

    user_tickets, user_ages = prep_tickets(user_tickets)
    worker_tickets, worker_ages = prep_tickets(worker_tickets)

    return JsonResponse({'user_tickets': {'tickets': [elem.serialize() for elem in user_tickets] if user_tickets else None,'ages': user_ages},
                        'worker_tickets': {'tickets': [elem.serialize() for elem in worker_tickets] if worker_tickets else None, 'ages': worker_ages}
                         }, safe=False)


def my_dashboard(request):
    pass


def profile(request, username):
    pass


def archive(request, operation="init"):
    if operation == "get":
        user = User.objects.get(username=request.user)
        tickets = []
        ages = []
        if user.permission == User.Permission.User:
            tickets = Ticket.objects.filter(owner=user)
            tickets, ages = prep_tickets(tickets)
        else:
            tickets = Ticket.objects.all()
            tickets, ages = prep_tickets(tickets)

        return JsonResponse({'tickets': [ticket_.serialize() for ticket_ in tickets],
                             'age': ages}, safe=False)
    else:
        return render(request,'archive.html')


def close_ticket(request, id):
    user = request.user
    user = User.objects.get(username=user)
    ticket = Ticket.objects.get(id=id)

    if not ticket:
        return JsonResponse({
            "message": "Ticket does not exist!",
            'error': True
        })
    if user.permission != User.Permission.Lead_Worker and user != ticket.owner and user != ticket.assigned_to:
        return JsonResponse({
            "message": PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    ticket.closed = True
    ticket.save()

    entry = LogEntry()
    entry.content = f"Ticket({ticket.id}) has been closed by {request.user}"
    entry.ticket = ticket
    entry.type = LogEntry.Type.Notification
    entry.save()

    return JsonResponse({
        "message": "Ticket has been closed",
        'error': False
    })


def claim_ticket(request):
    active_user = request.user

    if active_user.is_anonymous:
        return JsonResponse({
            "message": "You have to be logged in to do that!",
            'error': True
        })

    user = User.objects.get(username=active_user)

    if user.permission != User.Permission.Lead_Worker and user.permission != User.Permission.Worker:
        return JsonResponse({
            "message": PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    data = json.loads(request.body)

    ticket = data.get('ticket')
    ticket = Ticket.objects.get(id=ticket['id'])

    if ticket.assigned_to and user.permission != User.Permission.Lead_Worker:
        return JsonResponse({
            "message": PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    ticket.assigned_to = user
    ticket.save()

    entry = LogEntry()
    entry.content = f"Ticket({ticket.id}) has been claimed by {ticket.assigned_to.username}"
    entry.ticket = ticket
    entry.type = LogEntry.Type.Notification
    entry.save()

    return JsonResponse({
        "message": "Ticket successfully claimed!",
        'error': False
    })


def ticket(request, id):

    user = request.user
    user_ = User.objects.get(username=user)
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
        'ticket': ticket_to_display.serialize(),
        'age': age,
    })


def get_all_tickets(request):
    tickets = Ticket.objects.all()
    tickets, ages = prep_tickets(tickets)

    return JsonResponse({'tickets': [ticket_.serialize() for ticket_ in tickets], 'age': ages}, safe=False)


# TODO: Maybe error ahndling
@login_required
def get_all_entries_for_ticket(request, ticket_id):
    logs = Ticket.objects.get(id=ticket_id).log_entries
    logs = logs.order_by('-timestamp').all()
    return JsonResponse({'entries': [entry.serialize() for entry in logs]}, safe=False)


def new_comment(request):

    validate = form_standard_check(request, "comment")
    if validate:
        return validate

    data = json.loads(request.body)
    ticket_id = data.get('ticket')

    if not Ticket.objects.filter(id=ticket_id).exists():
        return JsonResponse({
            "message": "Something went wrong! This ticket does not exist anymore!",
            'error': True
            })

    entry = LogEntry()
    entry.owner = request.user
    entry.content = data.get('content')
    entry.type = 'Comment'
    entry.ticket = Ticket.objects.get(id=ticket_id)
    entry.save()

    return JsonResponse({
        "message": "Ticket created successfully.",
        'ticket': entry.serialize(),
        'error': False
    }, safe=False)


# TODO: Nicht SPA redirect ersetzen durch js verhalten
# TODO: Remove age + ticket if not needed
@csrf_exempt
@login_required
def new_ticket(request):
    validate = form_standard_check(request, "ticket")
    if validate:
        return validate

    data = json.loads(request.body)

    newticket = Ticket()
    newticket.owner = request.user
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
