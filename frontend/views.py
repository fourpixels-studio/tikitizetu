from django.db.models import Count
from django.shortcuts import render
from .models import Testimonial, HomePage
from events.models import Event, EventCategory


def index(request):
    category = request.GET.get('category')
    if category is not None:
        events = Event.objects.filter(category__slug=category).order_by("-pk")
    else:
        events = Event.objects.order_by("-pk")
    active_category = request.GET.get('category', None)

    context = {
        "events": events,
        'category_name': "All",
        "active_category": active_category,
        "homepage": HomePage.objects.first(),
        "title_tag": "Your Ultimate Event Ticketing Platform",
        "testimonials": Testimonial.objects.filter(post_testimonial=True),
        "categories": EventCategory.objects.annotate(event_count=Count('event')).filter(event_count__gt=0),
        "categories_count": EventCategory.objects.annotate(event_count=Count('event')).filter(event_count__gt=0).count(),
    }
    return render(request, "index.html", context)


def contact(request):
    context = {
        "title_tag": "Contact",
    }
    return render(request, "contact.html", context)


def about(request):
    context = {
        "title_tag": "About",
    }
    return render(request, "about.html", context)
