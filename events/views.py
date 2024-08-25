from django.shortcuts import render, get_object_or_404
from .models import Event


def events_list(request):
    context = {
        "title_tag": "Events",
        "events": Event.objects.order_by("-pk"),
    }
    return render(request, "events_list.html", context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {
        "title_tag": event.name,
        "event": event,
        "upcoming_events": Event.objects.order_by("-pk"),
    }
    return render(request, "event_detail.html", context)


def search_events(request):
    context = {
        "title_tag": f'"{request.GET.get("q")}" results',
    }
    return render(request, "events_list.html", context)
