from django.shortcuts import render
from events.models import Event


def index(request):
    context = {
        "title_tag": "Home",
        "events": Event.objects.order_by("-pk"),
    }
    return render(request, "index.html", context)


def contact(request):
    context = {
        "title_tag": "Contact",
    }
    return render(request, "contact.html", context)
