from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tickets", views.index, name="tickets"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("mytickets", views.my_tickets, name="mytickets"),
    path("mytickets/get", views.my_tickets_get, name="mytickets_get"),
    path("mydashboard", views.my_dashboard, name="mydashboard"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("ticket/<int:id>", views.ticket, name="ticket"),
    path("getalltickets", views.get_all_tickets, name="getalltickets"),
    path("newticket", views.new_ticket, name="newticket"),
    path("newcomment", views.new_comment, name="newcomment"),
    path("getallentries/<int:ticket_id>", views.get_all_entries_for_ticket, name="getallentries"),
]