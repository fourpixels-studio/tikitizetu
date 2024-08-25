from django.urls import path
from .views import events_list, event_detail, search_events

urlpatterns = [
    path("", events_list, name="events_list"),
    path("<int:pk>/", event_detail, name="event_detail"),
    path("search/results/", search_events, name="search_events"),
]
