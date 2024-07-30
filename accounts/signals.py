from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.base import ContentFile
from .models import CustomUser

def optimize_image(image_file, size=None):
    try:
        image = PilImage.open(image_file)
        if size:
            image = image.resize(size, PilImage.ANTIALIAS)

        image = image.convert('RGB')
        optimized_image_io = BytesIO()
        image.save(optimized_image_io, format='JPEG', quality=85)

        return ContentFile(optimized_image_io.getvalue(), image_file.name)
    except Exception as e:
        print(f'Error optimizing image: {e}')
        return None

@receiver(post_save, sender=CustomUser)
def optimize_profile_images(sender, instance, **kwargs):
    if instance.profile_picture:
        optimized_picture = optimize_image(instance.profile_picture, (300, 300))
        if optimized_picture:
            instance.profile_picture.save(instance.profile_picture.name, optimized_picture, save=False)
    if instance.profile_banner:
        optimized_banner = optimize_image(instance.profile_banner, (1600, 600))
        if optimized_banner:
            instance.profile_banner.save(instance.profile_banner.name, optimized_banner, save=False)
