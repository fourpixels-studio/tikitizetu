from django.urls import path
from .views import cart

urlpatterns = [
    path("<slug:slug>/<int:pk>", cart, name="cart"),
]
