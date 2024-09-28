from django.contrib import admin
from .models import Event, TicketCategory, EventCategory
admin.site.register(Event)
admin.site.register(EventCategory)
admin.site.register(TicketCategory)
