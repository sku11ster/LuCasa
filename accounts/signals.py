from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .models import CustomUser

def optimize_image(image, max_size):
    image = Image.open(image)
    image = image.convert('RGB')

    image.thumbnail(max_size, Image.ANTIALIAS)

    output = BytesIO()
    image.save(output, format='JPEG', quality=85)
    output.seek(0)
    return ContentFile(output.read(), image.name)

@receiver(post_save, sender=CustomUser)
def optimize_profile_images(sender, instance, **kwargs):
    if instance.profile_picture:
        instance.profile_picture.save(
            instance.profile_picture.name,
            optimize_image(instance.profile_picture, (300, 300)),
            save=False
        )
    if instance.profile_banner:
        instance.profile_banner.save(
            instance.profile_banner.name,
            optimize_image(instance.profile_banner, (1600, 600)),
            save=False
        )
