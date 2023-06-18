from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("tickets", views.index, name="tickets"),

    path("mytickets", views.my_tickets, name="mytickets"),
    path("mytickets/<str:operation>/<int:page_number>", views.my_tickets_get, name="mytickets_get"),

    path("mydashboard", views.my_dashboard, name="mydashboard"),
    path("mydashboard/<str:operation>", views.my_dashboard, name="mydashboard"),

    path("myteam", views.my_team, name="myteam"),
    path("myteam/<str:operation>", views.my_team, name="myteam"),
    path("myteam/<str:operation>/<int:page_number>", views.my_team, name="myteam"),

    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/<str:operation>", views.profile, name="profile"),
    path("profile/<str:username>/<str:operation>/<int:page_number>", views.profile, name="profile"),

    path("ticket/<int:id>", views.ticket, name="ticket"),
    path("ticket/<int:id>/close", views.close_ticket, name="closeticket"),
    path("ticket/<int:id>/reassign", views.reassign_ticket, name="reassignticket"),
    path("ticket/<int:id>/claim", views.claim_ticket, name="claimticket"),

    path("getalltickets", views.get_all_tickets, name="getalltickets"),
    path("getalltickets/<int:page_number>", views.get_all_tickets, name="getalltickets"),

    path("newticket", views.new_ticket, name="newticket"),

    path("newcomment", views.new_comment, name="newcomment"),

    path("getallentries/<int:ticket_id>", views.get_all_entries_for_ticket, name="getallentries"),
    path("getallentries/<int:ticket_id>/<int:page_number>", views.get_all_entries_for_ticket, name="getallentries"),


    path("archive", views.archive, name="archive"),
    path("archive/<str:operation>", views.archive, name="archive"),
    path("archive/<str:operation>/<int:page_number>", views.archive, name="archive"),

    path("createworker", views.create_worker, name="createworker"),
    path("createteam", views.create_team, name="createteam"),
]
