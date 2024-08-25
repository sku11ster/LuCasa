from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import PropertyImage,PropertyVideo,Property,Transaction

@receiver(post_save, sender=PropertyImage)
@receiver(post_delete, sender=PropertyImage)
def property_images(sender, instance, **kwargs):
    property_instance = instance.property
    image_paths = property_instance.images.values_list('image', flat=True)
    property_instance.image_paths = ','.join(image_paths)
    property_instance.save()


@receiver(post_save, sender=PropertyVideo)
@receiver(post_delete, sender=PropertyVideo)
def property_videos(sender, instance, **kwargs):
    property_instance = instance.property
    video_paths = property_instance.videos.values_list('video', flat=True)
    property_instance.video_paths = ','.join(video_paths)
    property_instance.save()


@receiver(post_save, sender=Property)
def create_listed_transaction(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(
            property=instance,
            seller=instance.user,
            transaction_type='list',
            amount=instance.price  
        )