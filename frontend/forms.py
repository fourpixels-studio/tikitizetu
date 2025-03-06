from django import forms
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'review', 'stars']
        widgets = {
            'stars': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }
