from django.urls import path
from .views import index, contact, submit_testimonial

urlpatterns = [
    path("", index, name="index"),
    path("contact/", contact, name="contact"),
    path('submit-testimonial/', submit_testimonial, name='submit_testimonial'),
]
