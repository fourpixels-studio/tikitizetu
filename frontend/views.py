from django.shortcuts import render


def index(request):
    context = {
        "title_tag": "Home",
    }
    return render(request, "index.html", context)
