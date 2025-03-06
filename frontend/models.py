from django.db import models


class Testimonial(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    testimonial = models.TextField(blank=True, null=True)
    post_testimonial = models.BooleanField(default=True)
    pub_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    image_link = models.TextField(blank=True, null=True)
    stars = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.name}' Testimonial - Posted On: {self.pub_date.strftime('%A, %B %d, %Y')}"
