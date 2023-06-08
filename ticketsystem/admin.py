from django.contrib import admin
from .models import User, Ticket, LogEntry, Team

# Register your models here.
admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(LogEntry)
admin.site.register(Team)
