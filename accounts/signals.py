from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def optimize_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        image = Image.open(instance.profile_picture)
        image = image.convert('RGB')

        image.thumbnail((800, 800), Image.ANTIALIAS)

        output = BytesIO()
        image.save(output, format='JPEG', quality=85)
        output.seek(0)
        instance.profile_picture.save(
            instance.profile_picture.name,
            ContentFile(output.read()),
            save=False
        )
        output.close()
