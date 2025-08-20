from django.db import models
from muse.models import Song, User, ArtistProfile
from django.core.cache import cache
from datetime import datetime, timedelta

class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='method_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('pending','Pending'),('success','Success'),('failed','Failed')])

    def __str__(self):
        return f'{self.song.song_name} - {self.amount} bought by {self.user}'

    def calculate_commission(self):
        rate = 0.15
        commission_amount = self.amount * rate
        return commission_amount
    def tax(self):
        rate = 0.15
        tax_amount = self.amount * rate
        return tax_amount

    def artist_earnings(self):
        commission = self.calculate_commission()
        tax = self.tax()
        earnings = self.amount - commission - tax
        return earnings

    def redirect_if_success(self):
        """Redirects to download page if payment succeeded."""
        if self.status == 'success':
            return redirect(reverse('song_download', args=[self.song.id]))
        return

class ArtistEarnings(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE,related_name='artist_earnings')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='artist_earnings_payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account = models.CharField(max_length=10, choices = [('credit', 'Credit'),('debit', 'Debit')], default='credit')

    def __str__(self):
        return f'{self.artist.user} - {self.amount}'

class ArtistShare(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='song_artist_share')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='artist_song_share')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_earnings_share')
    percentage = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.artist.user} - {self.amount}'


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


def get_artist_streams(user):
    artist_streams = cache.get('artist_streams')
    if artist_streams is None:

        cache.set('artist_streams', artist_streams, 60 * 60 * 24)
    return artist_streams

def get_best_songs(user):
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    trending_songs = cache.get(f'{user}_best_artist_songs')
    if trending_songs is None:
        trending_songs = Song.published.filter(artist=user).annotate(
            likes_count = models.Count('likes'),
            streams_count = models.Count('play_count'),
            score=models.F('likes_count') * 2 + models.F('streams_count')
        ).order_by('-score')[:10]
        cache.set(f'{user}_best_artist_songs', trending_songs, 60*60)
    return trending_songs
