from django.db import models

from muse.models import Song, User
from django.core.cache import cache
from datetime import datetime, timedelta

class Sales(models.Model):
    choices = (('approved','Approved'),('pending','Pending'),('rejected','Rejected'))
    payment_choices = (('Ecocash USD','Ecocash USD'),('Ecocash ZIG','Ecocash ZIG'),('InnBucks','InnBucks'),
                       ('VISA/Mastercard','VISA/Mastercard'))
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_sales')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True ,related_name='user_sales')
    artist = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sales')
    email = models.EmailField(default='sales@ingoma.com')
    phone = models.CharField(max_length=14, null=True)
    poll_url = models.CharField(max_length=100, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=1)
    status = models.CharField(choices=choices, max_length=50, default='approved')
    created = models.DateTimeField(auto_now_add=True)
    cleared = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'sale'
        verbose_name_plural = 'sales'
        ordering = ('created',)

    def __str__(self):
        return f'song bought {self.song} for {self.amount}'

    objects = models.Manager()

class News_and_Updates(models.Model):
    choices = (('draft','draft'),('published','published'))
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='news_and_updates/')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=11, choices=choices)

    class Meta:
        verbose_name = 'Update'
        verbose_name_plural = 'Updates'

    def __str__(self):
        return self.title
class Song_Payments(models.Model):
    choices = (('success','success'),('failed', 'failed'))
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments')
    amount = models.DecimalField(decimal_places=2, max_digits=11)
    payment_status = models.CharField(max_length=10, choices=choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Song Payment'
        verbose_name_plural = 'Song Payments'

    def __str__(self):
        return 'Song Payment Updated'


def get_artist_streams(user):
    artist_streams = cache.get('artist_streams')
    if artist_streams is None:

        cache.set('artist_streams', artist_streams, 60 * 60 * 24)
    return artist_streams

def get_best_songs(user):
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    trending_songs = cache.get('best_artist_songs')
    if trending_songs is None:
        trending_songs = Song.published.filter(artist=user).annotate(
            likes_count = models.Count('likes'),
            streams_count = models.Count('play_count'),
            score=models.F('likes_count') * 2 + models.F('streams_count')
        ).order_by('-score')[:10]
        cache.set('best_artist_songs', trending_songs, 60*60)
    return trending_songs
