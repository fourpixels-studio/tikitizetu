from django.db import models
from django.templatetags.static import static


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

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_link:
            return self.image_link
        return static('tikitizetu_square_thumbnail.jpg')
        
    def __str__(self):
        return f"{self.name}' Testimonial - Posted On: {self.pub_date.strftime('%A, %B %d, %Y')}"


class HomePage(models.Model):
    hero_h1 = models.CharField(max_length=200, blank=True, null=True)
    hero_paragraph = models.CharField(max_length=200, blank=True, null=True)
    hero_primary_btn = models.CharField(max_length=70, blank=True, null=True)
    hero_secondary_btn = models.CharField(max_length=70, blank=True, null=True)
    hero_image_1200 = models.FileField(upload_to="homepage/", blank=True, null=True)
    hero_image_992 = models.FileField(upload_to="homepage/", blank=True, null=True)
    hero_image_576 = models.FileField(upload_to="homepage/", blank=True, null=True)
    
    step_1_title = models.CharField(max_length=100, blank=True, null=True)
    step_1_paragraph = models.CharField(max_length=200, blank=True, null=True)
    step_1_image_1200 = models.FileField(upload_to="homepage/", blank=True, null=True)
    step_1_image_992 = models.FileField(upload_to="homepage/", blank=True, null=True)
    step_1_image_576 = models.FileField(upload_to="homepage/", blank=True, null=True)
    
    step_2_title = models.CharField(max_length=100, blank=True, null=True)
    step_2_paragraph = models.CharField(max_length=200, blank=True, null=True)
    step_2_image_1200 = models.FileField(upload_to="homepage/", blank=True, null=True)
    step_2_image_992 = models.FileField(upload_to="homepage/", blank=True, null=True)
    step_2_image_576 = models.FileField(upload_to="homepage/", blank=True, null=True)
    
    step_3_title = models.CharField(max_length=100, blank=True, null=True)
    step_3_paragraph = models.CharField(max_length=200, blank=True, null=True)
    step_3_image_1200 = models.FileField(upload_to="homepage/", blank=True, null=True)
    step_3_image_992 = models.FileField(upload_to="homepage/", blank=True, null=True)
    step_3_image_576 = models.FileField(upload_to="homepage/", blank=True, null=True)
    
    events_title = models.CharField(max_length=100, blank=True, null=True)
    
    why_choose_us = models.CharField(max_length=200, blank=True, null=True)
    
    reason_1_title = models.CharField(max_length=80, blank=True, null=True)
    reason_1_icon = models.CharField(max_length=70, blank=True, null=True)
    reason_1_paragraph = models.CharField(max_length=200, blank=True, null=True)
    
    reason_2_title = models.CharField(max_length=80, blank=True, null=True)
    reason_2_icon = models.CharField(max_length=70, blank=True, null=True)
    reason_2_paragraph = models.CharField(max_length=200, blank=True, null=True)
    
    reason_3_title = models.CharField(max_length=80, blank=True, null=True)
    reason_3_icon = models.CharField(max_length=70, blank=True, null=True)
    reason_3_paragraph = models.CharField(max_length=200, blank=True, null=True)
    
    reason_4_title = models.CharField(max_length=80, blank=True, null=True)
    reason_4_icon = models.CharField(max_length=70, blank=True, null=True)
    reason_4_paragraph = models.CharField(max_length=200, blank=True, null=True)
    
    sell_tickets_banner_title = models.CharField(max_length=100, blank=True, null=True)
    sell_tickets_banner_paragraph = models.CharField(max_length=200, blank=True, null=True)
    sell_tickets_banner_btn = models.CharField(max_length=50, blank=True, null=True)
    sell_tickets_banner_image_1200 = models.FileField(upload_to="homepage/", blank=True, null=True)
    sell_tickets_banner_image_992 = models.FileField(upload_to="homepage/", blank=True, null=True)
    sell_tickets_banner_image_576 = models.FileField(upload_to="homepage/", blank=True, null=True)

    testimonials_title = models.CharField(max_length=100, blank=True, null=True)
    
    newsletter_banner_title = models.CharField(max_length=70, blank=True, null=True)
    newsletter_banner_paragraph = models.CharField(max_length=200, blank=True, null=True)
    newsletter_banner_btn = models.CharField(max_length=50, blank=True, null=True)
    newsletter_image = models.FileField(upload_to="homepage/", blank=True, null=True)

    def __str__(self):
        return "Home Page"
