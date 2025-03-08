from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField


class Host(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='host')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    square_thumbnail = ResizedImageField(size=[150, 150], crop=['middle', 'center'],quality=75, upload_to='account/', blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=25, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    @property
    def get_phone_number(self):
        if self.phone_number:
            return self.phone_number
        return "N/A"

    @property
    def get_first_name(self):
        name = "N/A"
        if self.user.first_name:
            name = self.user.first_name
        elif self.user.last_name:
            name = self.user.last_name
        return name

    @property
    def get_email(self):
        if self.user.email:
            return self.user.email
        return "N/A"

    def save(self, *args, **kwargs):
        if self.profile_picture:
            if not self.pk:
                super().save(*args, **kwargs)
            if not self.square_thumbnail or self.square_thumbnail.name != f"{self.profile_picture.name}":
                self.square_thumbnail.save(f"{self.profile_picture.name}", self.profile_picture, save=False)
        super().save(*args, **kwargs)
