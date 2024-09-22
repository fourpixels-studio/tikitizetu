from django.db import models
from events.models import Event
from django.urls import reverse


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=100, unique=True)
    order_tracking_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_code = models.CharField(max_length=20, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    paid = models.BooleanField(default=False, blank=True, null=True)
    ticket_type = models.CharField(max_length=30, blank=True, null=True)
    num_tickets = models.CharField(max_length=20, default=1, null=True, blank=True)
    amount = models.CharField(max_length=5, default=0)
    qr = models.FileField(upload_to='qrcodes/', blank=True, null=True)
    pdf_ticket = models.FileField(upload_to='tickets/', max_length=100, null=True, blank=True)
    payment_date = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=70, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, blank=True, null=True)

    @property
    def get_event(self):
        if self.event:
            return self.event
        return "N/A"

    @property
    def get_phone_number(self):
        if self.phone_number:
            return self.phone_number
        return "N/A"

    @property
    def get_fullname(self):
        if self.first_name:
            first_name = self.first_name
        else:
            first_name = "John"
        if self.last_name:
            last_name = self.last_name
        else:
            last_name = "Doe"
        return str(f"{first_name} {last_name}")

    @property
    def get_email(self):
        if self.email:
            return self.email
        return "N/A"

    @property
    def get_url(self):
        return reverse("view_ticket", kwargs={
            "event_name": self.event.slug,
            "ticket_number": self.ticket_number,
            "event_id": self.event.pk,
        })

    @property
    def get_payment_method(self):
        if self.payment_mode:
            if self.payment_mode == 'pesapal':
                if self.mpesa_code:
                    payment_mode = "M-Pesa"
                else:
                    payment_mode = "Card"
            else:
                payment_mode = "M-Pesa"
            return payment_mode
        return "N/A"

    @property
    def get_transaction_code(self):
        if self.payment_mode:
            if self.payment_mode == 'pesapal':
                if self.mpesa_code:
                    transaction_code = self.mpesa_code
                else:
                    transaction_code = self.order_tracking_id[:10]
            else:
                transaction_code = self.mpesa_code
            return transaction_code
        return "N/A"

    @property
    def get_qr(self):
        if self.paid:
            if self.qr:
                return self.qr.url
        return None

    @property
    def get_pdf_ticket(self):
        if self.paid:
            if self.pdf_ticket:
                return self.pdf_ticket.url
        return None

    @property
    def get_reference_number(self):
        if self.event:
            return f"{self.event.pk}{self.pk}"
        return "N/A"

    def __str__(self):
        if self.paid:
            status = f"Paid via {self.get_payment_method}"
        else:
            status = f"NOT PAID: {self.status}"
        return f"{self.first_name} {self.last_name}'s ticket | Status: {status}"
