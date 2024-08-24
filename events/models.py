from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Event(models.Model):
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
    # host = models.CharField(max_length=200, null=True, blank=True)
    # likes = models.CharField(default=0, max_length=9, null=True, blank=True)
    # map = models.TextField(null=True, blank=True)

    @property
    def get_url(self):
        return reverse("event_detail", kwargs={
            "slug": self.slug
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class EventParticipant(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    ticket_number = models.CharField(
        max_length=36, unique=True, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f"{self.first_name} {self.last_name} | {self.event}"
