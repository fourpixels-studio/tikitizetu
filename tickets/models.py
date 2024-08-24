from django.db import models
from events.models import Event
from django.urls import reverse


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    amount = models.CharField(max_length=5)
    qr = models.FileField(max_length=100)
    scan_count = models.PositiveIntegerField(default=0)

    @property
    def get_event(self):
        if self.event:
            return self.event
        return None

    @property
    def get_url(self):
        return reverse("ticket_detail", kwargs={
            "event_name": self.event.slug,
            "ticket_number": self.ticket_number,
        })

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s ticket | {self.ticket_number} | Scanned {self.scan_count} times | Event: {self.event}"