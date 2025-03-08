from django.db import models
from hosts.models import Host
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django_resized import ResizedImageField
from django.templatetags.static import static


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
    square_poster = models.ImageField(upload_to="events_posters/", blank=True, null=True)
    landscape_poster = models.ImageField(upload_to="events_posters/", blank=True, null=True)
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
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='host', blank=True, null=True)
    likes = models.CharField(default=0, max_length=9, null=True, blank=True)
    map = models.TextField(null=True, blank=True)
    meta_thumbnail = ResizedImageField(size=[1200, 630], crop=['middle', 'center'],quality=75, upload_to='events_posters/thumbnails/', blank=True, null=True)
    square_thumbnail = ResizedImageField(size=[876, 876], quality=75, upload_to='events_posters/thumbnails/', blank=True, null=True)

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
        if not self.slug:
            self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)
        if self.landscape_poster and (not self.meta_thumbnail or self.meta_thumbnail.name != f"{self.landscape_poster.name}"):
            self.meta_thumbnail.save(f"{self.landscape_poster.name}", self.landscape_poster, save=False)
            super(Event, self).save(update_fields=['meta_thumbnail'])
        if self.square_poster and (not self.square_thumbnail or self.square_thumbnail.name != f"{self.square_poster.name}"):
            self.square_thumbnail.save(f"{self.square_poster.name}", self.square_poster, save=False)
            super(Event, self).save(update_fields=['square_thumbnail'])

    @property
    def get_meta_thumbnail(self):
        if self.meta_thumbnail:
            return self.meta_thumbnail.url
        return static('tikiti_zetu_meta_thumbnail.jpg')

    @property
    def get_square_thumbnail(self):
        if self.square_thumbnail:
            return self.square_thumbnail.url
        return static('tikitizetu_square_thumbnail.jpg')

    @property
    def get_landscape_poster(self):
        if self.landscape_poster:
            return self.landscape_poster.url
        return static('tikiti_zetu_meta_thumbnail.jpg')

    @property
    def get_square_poster(self):
        if self.square_poster:
            return self.square_poster.url
        return static('tikitizetu_square_thumbnail.jpg')

    @property
    def get_location(self):
        venue = ""
        location = ""
        if self.venue:
            venue += self.venue
        if self.location:
            location += self.location
        return f"{venue}, {location}"
        
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
