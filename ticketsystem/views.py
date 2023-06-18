import json
from django.db import models

from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q

from django.core.paginator import Paginator

from datetime import datetime, timezone
import datetime

from django.contrib.auth.decorators import login_required

from .models import User, Ticket, LogEntry, Team

PERMISSION_DENIED_MESSAGE = "You do not have the permission to do that!"
TICKET_NOT_EXIST_MESSAGE = "Ticket does not exist!"
PER_PAGE = 5


# Helper Functions
# Returns number of days
def calc_age(date):
    now = datetime.datetime.now(timezone.utc)
    delta = now - date
    return delta.days if delta.days else 0


# Every return value other than None implying that something went wrong and the result should be returned
def form_standard_check(request, to_be_created):
    if request.method != 'POST':
        return JsonResponse({
            "message": f"Something went wrong while creating a {to_be_created}!",
            'error': True
        })

    user = request.user
    if user.is_anonymous:
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


# needs model array (something like "tickets") and page_number
# returns first serialized elem array and then current page number, has_next, has_previous and total page count
def pagination(model_array, page_number):
    paginator = Paginator(model_array, PER_PAGE)
    model = paginator.get_page(page_number)
    model.adjusted_elided_pages = paginator.get_elided_page_range(page_number)

    return [elem.serialize() for elem in model] if model else [],{
            "current": model.number,
            "has_next": model.has_next(),
            "has_previous": model.has_previous(),
            "total": model.paginator.num_pages
        }


@login_required()
def index(request):
    return render(request, "index.html")


@login_required()
def my_tickets(request):
    return render(request, "myticket.html")


@login_required()
def my_team(request, operation="init", page_number=1):

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
            'member': [member.serialize() for member in member] if member else [],
            'leader': [leader.serialize() for leader in leader] if leader else [],
            'error': False
        })

    elif operation == "tickets":

        member = list(member)
        member.extend(leader)
        tickets = Ticket.objects.none()

        for member_ in member:
            tickets = tickets | member_.assigned_tickets.all()
        tickets = tickets.filter(closed=False).all()
        tickets, ages = prep_tickets(tickets)
        tickets, page = pagination(tickets,page_number)

        return JsonResponse({
            'tickets': tickets,
            'page': page,
            'ages': ages,
            'error': False
        })

    else:
        return JsonResponse({
            "message": "Something went wrong!",
            'error': True
            })


@login_required()
def create_team(request):

    if request.method == "POST":

        if not request.user or request.user.permission != User.Permission.Lead_Worker:
            return render(request, "myteam.html", {
                'message': PERMISSION_DENIED_MESSAGE,
                'error': True,
            })
        creator = request.user

        if creator.leader_of is not None and len(Team.objects.get(name=creator.leader_of.name).leaders.all()) < 2:
            return render(request, "myteam.html", {
                'message': "Make sure that there is at least another leader in your current team!",
                'error': True,
            })

        team_name = request.POST['team_name']
        if team_name == "":
            return render(request, "myteam.html", {
                "message": "Please enter a team name!",
                'error': True,
            })
        if Team.objects.filter(name=team_name).exists():
            return render(request, "myteam.html", {
                "message": "Teamname already taken.",
                'error': True,
            })

        team = Team()
        team.name = team_name
        team.save()
        creator.leader_of = team
        creator.save()

        return HttpResponseRedirect(reverse("myteam"))
    else:
        return render(request, "myteam.html")

# adapted from register function see source at login_view!
@login_required()
def create_worker(request):
    if not request.user or request.user.permission != User.Permission.Lead_Worker:
        return render(request, "myteam.html", {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True,
        })

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        permission = request.POST['permission']

        if password != confirmation:
            return render(request, "myteam.html", {
                "message": "Passwords must match.",
                'error': True
            })

        try:
            user = User.objects.create_user(username, email, password)
            if permission != User.Permission.Lead_Worker and permission != User.Permission.Worker:
                return render(request, "myteam.html", {
                    "message": "Something went wrong while assigning the permission!",
                    'error': True,
                })

            user.permission = permission

            if permission == User.Permission.Lead_Worker:
                user.leader_of = request.user.leader_of
            else:
                user.member_of = request.user.leader_of

            user.save()
        except IntegrityError:
            return render(request, "myteam.html", {
                "message": "Username already taken.",
                'error': True,
            })
        return HttpResponseRedirect(reverse("myteam"))
    else:
        return render(request, "myteam.html")


@login_required()
def my_tickets_get(request, operation, page_number=1):
    user = request.user
    user = User.objects.get(username=user)

    tickets = Ticket.objects.none()

    if operation == 'user':
        tickets = Ticket.objects.filter(owner=user).all()
        tickets = tickets.filter(closed=False).all()

    if operation == 'worker' and (user.permission == User.Permission.Lead_Worker or user.permission == User.Permission.Worker):
        tickets = Ticket.objects.filter(assigned_to=user).all()
        tickets = tickets.filter(closed=False).all()

    tickets, ages = prep_tickets(tickets)

    tickets, page = pagination(tickets, page_number)

    return JsonResponse({'tickets': tickets, 'ages': ages, 'page': page}, safe=False)


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


@login_required()
def my_dashboard(request, operation='init'):
    user = request.user
    user = User.objects.get(username=user)

    if user.permission != User.Permission.Lead_Worker and user.permission != User.Permission.Worker:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    if operation == 'init':
        return render(request, "dashboard.html")

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


@login_required()
def profile(request, username, operation="init", page_number=1):
    if not User.objects.filter(username=username).exists():
        return HttpResponseRedirect(reverse('index'), {
            'message': "This user does not exist",
            'error': True
        })

    user_of_profile = User.objects.get(username=username)

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

        if request.user.permission == "User" and request.user != user_of_profile:
            tickets = tickets.filter(owner=request.user)

        tickets, ages = prep_tickets(tickets)
        tickets, page = pagination(tickets,page_number)
        return JsonResponse({
            'tickets': tickets,
            'ages': ages,
            'page': page
        })
    elif operation == "assigned":
        assigned_tickets = Ticket.objects.filter(assigned_to=user_of_profile, closed=False)

        if request.user.permission == "User" and request.user != user_of_profile:
            assigned_tickets = assigned_tickets.filter(owner=request.user)

        assigned_tickets, assigned_ages = prep_tickets(assigned_tickets)
        assigned_tickets, page = pagination(assigned_tickets, page_number)

        return JsonResponse({
            'tickets': assigned_tickets,
            'ages': assigned_ages,
            'page': page
        })


@login_required()
def archive(request, operation="init", page_number=1):
    if operation == "get":
        user = User.objects.get(username=request.user)

        if user.permission == User.Permission.User:
            tickets = Ticket.objects.filter(owner=user)

        else:
            tickets = Ticket.objects.all()

        tickets = tickets.filter(closed=True).all()

        tickets, ages = prep_tickets(tickets)
        tickets, page = pagination(tickets, page_number)

        return JsonResponse({'tickets': tickets, 'page': page, 'age': ages}, safe=False)
    else:
        return render(request, 'archive.html')


@login_required()
def reassign_ticket(request, id):
    user = request.user

    if user.permission != User.Permission.Lead_Worker:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    if not Ticket.objects.filter(id=id).exists():
        return JsonResponse({
            "message": TICKET_NOT_EXIST_MESSAGE,
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


@login_required()
def close_ticket(request, id):
    user = request.user
    user = User.objects.get(username=user)

    if not Ticket.objects.filter(id=id).exists():
        return HttpResponseRedirect(reverse('index'), {
            "message": TICKET_NOT_EXIST_MESSAGE,
            'error': True
        })

    ticket = Ticket.objects.get(id=id)

    if user.permission != User.Permission.Lead_Worker and user != ticket.owner and user != ticket.assigned_to:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
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


@login_required()
def claim_ticket(request, id):
    user = request.user

    if user.permission != User.Permission.Lead_Worker and user.permission != User.Permission.Worker:
        return HttpResponseRedirect(reverse('index'), {
            'message': PERMISSION_DENIED_MESSAGE,
            'error': True
        })

    if not Ticket.objects.filter(id=id).exists():
        return HttpResponseRedirect(reverse('index'), {
            "message": TICKET_NOT_EXIST_MESSAGE,
            'error': True
        })

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


@login_required()
def ticket(request, id):

    if not Ticket.objects.filter(id=id).exists():
        return HttpResponseRedirect(reverse('index'), {
            "message": TICKET_NOT_EXIST_MESSAGE,
            'error': True
        })

    ticket_to_display = Ticket.objects.all().get(id=id)
    age = calc_age(ticket_to_display.timestamp)

    return render(request, "ticket.html", {
        'ticket': ticket_to_display.serialize(),
        'age': age,
    })


@login_required()
def get_all_tickets(request, page_number=1):

    tickets = Ticket.objects.all()
    tickets = tickets.filter(closed=False).all()

    if request.user.permission == User.Permission.User:
        tickets = tickets.filter(owner=request.user)

    tickets, ages = prep_tickets(tickets)

    tickets, page = pagination(tickets, page_number)

    return JsonResponse({
        'tickets': tickets,
        "page": page,
        'age': ages,
    }, safe=False)


@login_required()
def get_all_entries_for_ticket(request, ticket_id, page_number=1):

    if not Ticket.objects.filter(id=ticket_id).exists():
        return HttpResponseRedirect(reverse('index'), {
            "message": TICKET_NOT_EXIST_MESSAGE,
            'error': True
        })

    logs = Ticket.objects.get(id=ticket_id).log_entries
    logs = logs.order_by('-timestamp').all()

    logs, page = pagination(logs, page_number)

    return JsonResponse({'entries': logs, 'page': page}, safe=False)


@login_required()
def new_comment(request):

    validate = form_standard_check(request, "comment")
    if validate:
        return validate

    data = json.loads(request.body)
    ticket_id = data.get('ticket')

    if not Ticket.objects.filter(id=ticket_id).exists():
        return JsonResponse({
            "message": TICKET_NOT_EXIST_MESSAGE,
            'error': True
            })

    entry = LogEntry()
    entry.owner = request.user
    entry.content = data.get('content')
    entry.image = data.get('image')
    entry.type = 'Comment'
    entry.ticket = Ticket.objects.get(id=ticket_id)
    entry.save()

    return JsonResponse({
        "message": "Ticket created successfully.",
        'ticket': entry.serialize(),
        'error': False
    }, safe=False)


@login_required()
def new_ticket(request):
    validate = form_standard_check(request, "ticket")
    if validate:
        return validate

    data = json.loads(request.body)

    newticket = Ticket()
    newticket.owner = request.user
    newticket.content = data.get('content')
    newticket.image = data.get('image')
    newticket.status = 'New'
    newticket.save()

    return JsonResponse({
        "message": "Ticket created successfully.",
        'error': False
    },  safe=False)


# Login/Logout/Register copied from Assignment 4 and slightly adapted
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
                "message": "Invalid username and/or password.",
                "error": True
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match.",
                'error': True
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken.",
                'error': True
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")
