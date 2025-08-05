from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ArtistProfile

@receiver(post_save, sender=User)
def create_artist_profile(sender, instance, created, **kwargs):
    if created and instance.is_artist:
        ArtistProfile.objects.create(user=instance)
    elif not created and instance.is_artist and not hasattr(instance, 'artistprofile'):
        ArtistProfile.objects.create(user=instance)