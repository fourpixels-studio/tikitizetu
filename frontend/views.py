from django.shortcuts import render
from events.models import Event, EventCategory


def index(request):
    category = request.GET.get('category')
    if category is not None:
        events = Event.objects.filter(category__slug=category).order_by("-pk")
    else:
        events = Event.objects.order_by("-pk")
    active_category = request.GET.get('category', None)

    context = {
        "title_tag": "Home",
        "events": events,
        'category_name': "All",
        "active_category": active_category,
        "categories": EventCategory.objects.all(),
    }
    return render(request, "index.html", context)


def contact(request):
    context = {
        "title_tag": "Contact",
    }
    return render(request, "contact.html", context)
