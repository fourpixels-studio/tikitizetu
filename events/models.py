from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify


class EventCategory(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    @property
    def get_url(self):
        return reverse("events_list", kwargs={
            "slug": self.slug,
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Event(models.Model):
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    poster = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    event_disclaimer = models.TextField(null=True, blank=True)
    event_keywords = models.TextField(null=True, blank=True)
    event_description = models.TextField(null=True, blank=True)
    event_capacity = models.IntegerField(default=50, null=True, blank=True)
    confirmation_email_subject = models.TextField(null=True, blank=True)
    confirmation_email_message = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    host = models.CharField(max_length=200, null=True, blank=True)
    likes = models.CharField(default=0, max_length=9, null=True, blank=True)
    map = models.TextField(null=True, blank=True)

    @property
    def get_share_link(self):
        current_site = settings.MY_SITE
        event_url = self.get_url
        return f"{current_site}{event_url}"

    @property
    def get_ticket_categories(self):
        if TicketCategory.objects.filter(event=self).exists():
            return TicketCategory.objects.filter(event=self)
        return None

    @property
    def get_ticket_price(self):
        if self.get_ticket_categories:
            return round(self.get_ticket_categories[0].price, 0)
        return None

    @property
    def get_url(self):
        return reverse("event_detail", kwargs={
            "slug": self.slug,
            "pk": self.pk,
        })
        
    @property
    def get_category_name(self):
        if self.category:
            return self.category.name
        return "All"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TicketCategory(models.Model):
    CATEGORY_CHOICES = [
        ('early_bird', 'Early Bird'),
        ('individual', 'Individual'),
        ('couple', 'Couple'),
        ('gate', 'Gate'),
        ('vip', 'VIP'),
        ('group_of_5', 'Group Of 5'),
        ('group_of_10', 'Group Of 10'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_categories')
    category_name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.IntegerField(default=0)
    tickets_sold = models.IntegerField(default=0)
    admits = models.CharField(max_length=35, blank=True, null=True)

    def __str__(self):
        return f"{self.get_category_name_display()} - {self.event.name}"
