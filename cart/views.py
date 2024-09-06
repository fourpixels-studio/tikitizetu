from django.shortcuts import render, get_object_or_404
from events.models import Event


def cart(request, slug, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {
        "title_tag": "Cart",
        "event": event,
    }
    return render(request, "cart.html", context)
