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
    assigned_to = models.ForeignKey("User", blank=True, null=True, on_delete=models.CASCADE,
                                    related_name="assigned_tickets")

    class Status(models.TextChoices):
        Done = "Done"
        Assigned = "Assigned"
        New = "New"

    status = models.CharField(choices=Status.choices, max_length=16)
    # type = models.ForeignKey("LogEntry", on_delete=models.CASCADE, null=True, blank=True, related_name='ticket')

    # TODO: Image sollten mehrere sein können
    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "image": self.image,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "log": [entry.id for entry in self.log_entries.all()],
            # "type": self.type.type if self.type else None,
        }


class LogEntry(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, blank=True, null=True, related_name="log_entries")
    content = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='log_entries')

    class Type(models.TextChoices):
        Comment = "Comment"
        Notification = "Notification"

    type = models.CharField(choices=Type.choices, max_length=16)

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username if self.type == "Comment" else "System",
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "type": self.type
        }
