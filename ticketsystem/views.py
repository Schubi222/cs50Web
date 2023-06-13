import json
from django.db import models

from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q

from datetime import datetime, timezone
import datetime

from django.contrib.auth.decorators import login_required

#TODO: For testing only
from django.views.decorators.csrf import csrf_exempt

from .models import User, Ticket, LogEntry, Team

PERMISSION_DENIED_MESSAGE = "You do not have the permission to do that!"


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


def permission_check(user, permission):
    if user.permission != permission:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True
        })
    return False


def index(request):
    return render(request, "index.html")


def my_tickets(request):
    return render(request, "myticket.html")


def my_team(request, operation="init"):

    if operation == "init":
        return render(request, "myteam.html")

    user = User.objects.get(username=request.user)

    if not user.member_of and not user.leader_of:
        return JsonResponse({
            'message': "You are not part of any team!",
            'error': True
        })

    team = user.member_of if user.member_of else user.leader_of

    member = User.objects.filter(member_of=team.name).all()
    leader = User.objects.filter(leader_of=team.name).all()

    if operation == "team":

        return JsonResponse({
            'member': [member.serialize() for member in member],
            'leader': [leader.serialize() for leader in leader],
            'error': False
        })

    elif operation == "tickets":

        member = list(member)
        member.extend(leader)
        tickets = Ticket.objects.none()

        for member_ in member:
            tickets = tickets | member_.assigned_tickets.all()
        tickets, ages = prep_tickets(tickets)

        tickets = tickets.filter(closed=False).all()

        return JsonResponse({
            'tickets': [ticket.serialize() for ticket in tickets],
            'ages': ages,
            'error': False
        })

    else:
        return JsonResponse({
            "message": "Something went wrong!",
            'error': True
            })


# TODO: Handle message; user.permission checken
def create_worker(request):
    if not request.user or request.user.permission != User.Permission.Lead_Worker:
        return render(request, "myteam.html", {
            'message': PERMISSION_DENIED_MESSAGE
        })
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        permission = request.POST['permission']

        if password != confirmation:
            return render(request, "myteam.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.permission = permission

            # add to the team of creator
            if permission == User.Permission.Lead_Worker:
                user.leader_of = request.user.leader_of
            else:
                user.member_of = request.user.leader_of

            user.save()
        except IntegrityError:
            return render(request, "myteam.html", {
                "message": "Username already taken."
            })
        return HttpResponseRedirect(reverse("myteam"))
    else:
        return render(request, "myteam.html")


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

    user_tickets = user_tickets.filter(closed=False).all()
    worker_tickets = worker_tickets.filter(closed=False).all()

    return JsonResponse({'user_tickets': {'tickets': [elem.serialize() for elem in user_tickets] if user_tickets else None,'ages': user_ages},
                        'worker_tickets': {'tickets': [elem.serialize() for elem in worker_tickets] if worker_tickets else None, 'ages': worker_ages}
                         }, safe=False)


def dashboard_get_tickets_last_30_days(user, closed, team=None, all_teams=False, not_assigned=False):
    if all_teams:
        if not_assigned:
            tickets = Ticket.objects.filter(assigned_to=None)
        else:
            tickets = Ticket.objects.filter(assigned_to=not None)
    elif team is not None:
        tickets = Ticket.objects.filter(Q(assigned_to__leader_of=team) | Q(assigned_to__member_of=team))
    else:
        tickets = Ticket.objects.filter(assigned_to=user).all()

    tickets = tickets.filter(closed=closed)

    now = datetime.datetime.now(timezone.utc)

    deadline_deltatime = datetime.timedelta(days=30)
    deadline = now - deadline_deltatime

    tickets_in_time = []

    for ticket in tickets:
        if ticket.closed_at_time and ticket.closed_at_time > deadline:
            tickets_in_time.append(ticket)

    return tickets_in_time if closed else tickets


# TODO: Potential für eigene angaben z.b. wie viele tage
def my_dashboard(request, operation='init'):
    if operation == 'init':
        return render(request, "dashboard.html")
    user = User.objects.get(username=request.user)
    team = user.leader_of if user.leader_of else user.member_of

    tickets_assigned_to_user_open = dashboard_get_tickets_last_30_days(user, False)
    tickets_assigned_to_user_closed = dashboard_get_tickets_last_30_days(user, True)

    if team:
        tickets_assigned_to_team_open = dashboard_get_tickets_last_30_days(user, False, team.name)
        tickets_assigned_to_team_closed = dashboard_get_tickets_last_30_days(user, True, team.name)

    tickets_all_open = dashboard_get_tickets_last_30_days(user, False, all_teams=True)
    tickets_all_closed = dashboard_get_tickets_last_30_days(user, True, all_teams=True)

    tickets_all_not_assigned = dashboard_get_tickets_last_30_days(user, False, all_teams=True, not_assigned=True)

    return JsonResponse({
        'Your open tickets': len(tickets_assigned_to_user_open),
        'Your closed tickets': len(tickets_assigned_to_user_closed),
        'Your team\'s open tickets': len(tickets_assigned_to_team_open) if team else "No Team",
        'Your team\'s closed tickets': len(tickets_assigned_to_team_closed) if team else "No Team",
        'All assigned tickets': len(tickets_all_open),
        'All closed tickets': len(tickets_all_closed),
        'All not assigned tickets': len(tickets_all_not_assigned),
    })


def profile(request, username, operation="init"):
    if not User.objects.filter(username=username).exists():
        return HttpResponseRedirect(reverse('index'), {
            'message': "This user does not exist",
            'error': True
        })

    user_of_profile = User.objects.get(username=username)

    if request.user.permission == "User" and request.user != user_of_profile:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    if operation == "init":
        return render(request, 'profile.html', {
            'user_of_profile': user_of_profile.serialize(),
        })

    elif operation == "infos":
        tickets = Ticket.objects.filter(owner=user_of_profile, closed=False)
        assigned_tickets = Ticket.objects.filter(assigned_to=user_of_profile)

        return JsonResponse({
            'ticket_count': len(tickets),
            'assigned_ticket_count': len(assigned_tickets),
        })
    elif operation == "ticket":
        tickets = Ticket.objects.filter(owner=user_of_profile, closed=False)
        tickets, ages = prep_tickets(tickets)

        return JsonResponse({
            'tickets': [elem.serialize() for elem in tickets] if tickets else [],
            'ages': ages,
        })
    elif operation == "assigned":
        assigned_tickets = Ticket.objects.filter(assigned_to=user_of_profile, closed=False)
        assigned_tickets, assigned_ages = prep_tickets(assigned_tickets)

        return JsonResponse({
            'tickets': [elem.serialize() for elem in assigned_tickets] if assigned_tickets else [],
            'ages': assigned_ages,
        })


def archive(request, operation="init"):
    if operation == "get":
        user = User.objects.get(username=request.user)

        tickets = []

        if user.permission == User.Permission.User:
            tickets = Ticket.objects.filter(owner=user)

        else:
            tickets = Ticket.objects.all()

        tickets, ages = prep_tickets(tickets)
        tickets = tickets.filter(closed=True).all()

        return JsonResponse({'tickets': [ticket_.serialize() for ticket_ in tickets],
                             'age': ages}, safe=False)
    else:
        return render(request,'archive.html')


def reassign_ticket(request, id):
    user = request.user

    if user.permission != User.Permission.Lead_Worker:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    if not Ticket.objects.filter(id=id).exists():
        return JsonResponse({
            "message": "Ticket does not exist!",
            'error': True
        })
    data = json.loads(request.body)
    assign_to = data['assign_to']

    ticket = Ticket.objects.get(id=id)

    ticket.assigned_to = None if assign_to == "unassign" else User.objects.get(username=assign_to)
    ticket.save()

    entry = LogEntry()
    if assign_to == "unassign":
        entry.content = f"Ticket({ticket.id}) has been removed from previous worker"
    else:
        entry.content = f"Ticket({ticket.id}) has been assigned to {ticket.assigned_to.username}"
    entry.ticket = ticket
    entry.type = LogEntry.Type.Notification
    entry.save()

    return JsonResponse({
        "message": f"Assigned to {data['assign_to']}",
        'error': False
    })


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
    ticket.status = Ticket.Status.Done
    ticket.closed_at_time = datetime.datetime.now(timezone.utc)
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


def claim_ticket(request, id):
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

    ticket = Ticket.objects.get(id=id)

    if ticket.assigned_to and user.permission != User.Permission.Lead_Worker:
        return JsonResponse({
            "message": PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    ticket.assigned_to = user
    ticket.status = Ticket.Status.Assigned
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
    tickets = tickets.filter(closed=False).all()
    tickets, ages = prep_tickets(tickets)

    return JsonResponse({'tickets': [ticket_.serialize() for ticket_ in tickets] if tickets else [], 'age': ages}, safe=False)


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
