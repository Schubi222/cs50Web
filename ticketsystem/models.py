from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="tickets")
    content = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.URLField(blank=True, null=True)
    assigned_to = models.ForeignKey("User", blank=True, null=True, on_delete=models.CASCADE, related_name="assigned_tickets")

    class Status(models.TextChoices):
        Done = "Done"
        Assigned = "Assigned"
        New = "New"

    status = models.CharField(choices=Status.choices, max_length=16)
    #TODO: Image sollten mehrere sien können
    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "image": self.image,
            "assigned_to": self.assigned_to,
            "status": self.status

        }