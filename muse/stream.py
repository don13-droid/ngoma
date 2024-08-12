from decimal import Decimal
from django.conf import settings
from .models import Song, Stream

class STREAM(object):
    def __init__(self, request):
        """
        Initialize the cart.
        """

        self.session = request.session
        stream = self.session.get(settings.STREAM_SESSION_ID)
        if not stream:
            # save an empty cart in the session
            stream = self.session[settings.STREAM_SESSION_ID] = {}
        self.stream = stream

    def add(self, song, user):
        """
        Add a product to the cart or update its quantity.
        """

        product_id = str(song.id)
        if product_id not in self.stream:
            self.stream[product_id] = {
                                     'song': str(song.id)}
            new_stream = Stream(
                song = song,
                user = user
            ).save()

        else:
            pass
        self.save()

    def save(self):

        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True