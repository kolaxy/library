from django.db import models
from django.contrib.auth.models import User, AbstractUser
from PIL import Image


class Profile(models.Model):

    def upload_to(self, filename):
        return f'profile_pics/{self.pk}/{filename}'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to=upload_to)

    def __str__(self):
        return f'Профиль {self.user.username}'

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
