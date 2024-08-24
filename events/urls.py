from django.urls import path
from .views import events_list, event_detail

urlpatterns = [
    path("", events_list, name="events_list"),
    path("<slug:slug>/", event_detail, name="event_detail"),
]
