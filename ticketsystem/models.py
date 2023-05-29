from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="tickets")
    content = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.URLField(blank=True)
    assigned_to = models.ForeignKey("User", blank=True, on_delete=models.CASCADE, related_name="assigned_tickets")

    class Status(models.TextChoices):
        Done = "Done"
        Assigned = "Assigned"
        New = "New"

    status = models.CharField(choices=Status.choices, max_length=16)

