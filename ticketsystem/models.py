from django.contrib.auth.models import AbstractUser
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=160, unique=True, primary_key=True)

    def serialize(self):
        return {
            "name": self.name,
            "leaders": [leader.username for leader in self.leaders.all()],
            "member": [member.username for member in self.members.all()],
        }


class User(AbstractUser):
    id = models.AutoField(primary_key=True)

    class Permission(models.TextChoices):
        User = "User"
        Worker = "Worker"
        Lead_Worker = "Lead_Worker"

    permission = models.CharField(choices=Permission.choices, max_length=16)
    leader_of = models.ForeignKey("Team", blank=True, null=True, on_delete=models.SET_NULL, related_name="leaders")
    member_of = models.ForeignKey("Team", blank=True, null=True, on_delete=models.SET_NULL, related_name="members")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "permission": self.permission,
            "member_of": self.member_of.name if self.member_of else None,
            "leader_of": self.leader_of.name if self.leader_of else None,
        }


class Ticket(models.Model):

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
    closed = models.BooleanField(default=False)
    closed_at_time = models.DateTimeField(blank=True, null=True)

    # TODO: Image sollten mehrere sein können
    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "image": self.image,
            "assigned_to": self.assigned_to.username if self.assigned_to else None,
            "status": self.status,
            "log": [entry.id for entry in self.log_entries.all()],
            "closed": self.closed,
            "closed_at_time": self.closed_at_time,

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
