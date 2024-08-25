from django.db import models
from events.models import Event
from django.urls import reverse


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    amount = models.CharField(max_length=5)
    num_tickets = models.CharField(max_length=2, blank=True, null=True)
    qr = models.FileField(upload_to='qrcodes/', max_length=100)
    pdf_ticket = models.FileField(
        upload_to='tickets/', max_length=100, null=True, blank=True)
    scan_count = models.PositiveIntegerField(default=0)

    @property
    def get_event(self):
        if self.event:
            return self.event
        return None

    @property
    def get_url(self):
        return reverse("view_ticket", kwargs={
            "event_name": self.event.slug,
            "ticket_number": self.ticket_number,
        })

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s ticket | {self.ticket_number} | Scanned {self.scan_count} times | Event: {self.event}"
