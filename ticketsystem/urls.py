from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tickets", views.index, name="tickets"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("mytickets", views.my_tickets, name="mytickets"),
    path("mydashboard", views.my_dashboard, name="mydashboard"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("ticket/<int:id>", views.ticket, name="ticket"),
    path("getalltickets", views.get_all_tickets, name="getalltickets")
]