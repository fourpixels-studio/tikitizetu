from .models import Event
from django.db.models import Q


def search_function(request):
    search_context = {}
    if request.GET:
        query = request.GET.get("q")
        if query:
            name_results = Q(name__icontains=query)
            location_results = Q(location__icontains=query)
            venue_results = Q(venue__icontains=query)
            event_keywords_results = Q(event_keywords__icontains=query)
            event_description_results = Q(event_description__icontains=query)

            results = Event.objects.filter(
                name_results | location_results |
                venue_results | event_keywords_results |
                event_description_results
            ).distinct()

        else:
            results = []

        num_results = len(results)

        search_context = {
            "events": results,
            "query": query,
            "num_results": num_results,
        }

    return search_context
