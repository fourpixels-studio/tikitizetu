from django import forms
from .models import Testimonial
from django_recaptcha.fields import ReCaptchaField


class TestimonialForm(forms.ModelForm):
    captcha = ReCaptchaField()
    class Meta:
        model = Testimonial
        fields = [
            'name',
            'email',
            'image',
            'stars',
            'captcha',
            'department',
            'testimonial',
            'post_testimonial',
        ]
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'post_testimonial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jane Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@website.com'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Beautiful Company'}),
            'testimonial': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 100px;', 'placeholder': 'Something nice :)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = False
        self.fields['image'].required = False
        self.fields['department'].required = True
        self.fields['testimonial'].required = True
        self.fields['post_testimonial'].required = False

    def clean_captcha(self):
        captcha_value = self.cleaned_data.get('captcha')
        if not captcha_value:
            raise forms.ValidationError("Please complete the captcha.")
        return captcha_value
