from django.db.models import Count
from .forms import TestimonialForm
from django.contrib import messages
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



def submit_testimonial(request):
    meta_description = str("Share your experience with us! Submit a testimonial and let others know about your thoughts and feedback.")
    meta_keywords = str("testimonials, customer reviews, feedback, user experience, submit testimonial")
    if request.method == 'POST':
        testimonial_form = TestimonialForm(request.POST, request.FILES)
        if testimonial_form.is_valid():
            testimonial_form.save()
            message = str("We appreciate you taking the time to share your experience. Your testimonial has been successfully submitted and will be published on our website. We value your feedback and thank you for your support!")
            messages.success(request, message)
            context = {
                "meta_keywords": meta_keywords,
                "meta_description": meta_description,
                'testimonial_form': TestimonialForm(),
                "title_tag": "Thank You For Sharing Your Experience With Us!",
            }
            return render(request, 'submit_testimonial.html', context)
        else:
            for field, errors in testimonial_form.errors.items():
                for error in errors:
                    messages.error(request, error)
            testimonial_form = TestimonialForm()
    context = {
        "meta_keywords": meta_keywords,
        "title_tag": "Submit a Testimonial",
        "meta_description": meta_description,
        'testimonial_form': TestimonialForm(),
    }
    return render(request, 'submit_testimonial.html', context)
