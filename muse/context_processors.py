# your_app/context_processors.py

def artist_profile(request):
    from .models import ArtistProfile
    if request.user.is_authenticated:
        try:
            artist_profile = ArtistProfile.objects.get(user=request.user)
        except ArtistProfile.DoesNotExist:
            artist_profile = None
    else:
        artist_profile = None
    return {'artist_profile': artist_profile}
