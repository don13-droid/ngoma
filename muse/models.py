from django.db import models
from django.db.models import Count, Sum, F, Q, Subquery, OuterRef
from django.contrib.auth.models import AbstractUser, Group
from django.conf import settings
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils.text import slugify
from django.core.validators import ValidationError,RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

MAX_UPLOAD_SIZE = 20971520  # 20MB in bytes
MAX_UPLOAD_SIZE_IMAGE = 5242880
def validate_file_size(value):
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(_('File size should not exceed 20MB.'))

def validate_image_size(value):
    if value.size > MAX_UPLOAD_SIZE_IMAGE:
        raise ValidationError(_('File size should not exceed 5MB.'))
class ExtensionValidator(RegexValidator):
    def __init__(self, extensions, message=None):
        if not hasattr(extensions, '__iter__'):
            extensions = [extensions]
        regex = '\.(%s)$' % '|'.join(extensions)
        if message is None:
            message = 'File type not supported. Accepted types are: %s.'%','.join(extensions)
        super(ExtensionValidator, self).__init__(regex,message)
    def __call__(self, value):
        super(ExtensionValidator, self).__call__(value.name)
# Create your models here.

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups',
        related_query_name = 'custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='custom_user',
    )
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    about_artist = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    facebook = models.CharField(max_length=250, blank=True, null=True)
    instagram = models.CharField(max_length=250, blank=True, null=True)
    x = models.CharField(max_length=250, blank=True, null=True)
    youtube = models.CharField(max_length=250, blank=True, null=True)
    is_artist = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_artist':True})
    verification_status = models.CharField(max_length=10, choices=[
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('bronze', 'Bronze'),
        ('none', 'None'),
    ], default='none')
    verification_requested = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username

    @property
    def verification_icon_color(self):
        if self.verification_status =='basic':
            return 'skyblue'
        elif self.verification_status == 'premium':
            return 'silver'
        elif self.verification_status == 'bronze':
            return 'gold'
        else:
            return None

    @property
    def verification_icon(self):
        return f'<i class="fa fa-check-circle" style="color: {self.verification_icon_color}"></i>'

    @property
    def display_name(self):
        if self.verification_icon_color:
            return f'{self.user.username} {self.verification_icon}'
        else:
            return self.user.username


class Genre(models.Model):
    name = models.CharField(max_length=500,
                            )

    def get_absolute_url(self):
        return reverse('muse:single_genre',
                       args=[self.name])

    class Meta:
        ordering = ('name',)
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name
    objects = models.Manager()

class Album(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500,
                            unique=True)
    genre = models.ForeignKey(Genre, related_name='album_genre',
                                 on_delete=models.CASCADE, default='')
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='albums')
    album_art = models.ImageField(upload_to='album_arts')
    about_album = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    released = models.CharField(max_length=20, choices=(('Released','Released'),('Draft','Draft')),
                                default='Released')
    album_latest = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=1)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('muse:single-album',
                       args=[self.name,
                             self.slug])

    class Meta:
        ordering = ('name',)
        verbose_name = 'album'
        verbose_name_plural = 'albums'

    def __str__(self):
        return self.name
    objects= models.Manager()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(is_draft=False)

class Song(models.Model):
    song_name = models.CharField(max_length=255)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='songs')
    album = models.ForeignKey(Album,on_delete=models.CASCADE,blank=True, null= True, related_name='albums')
    genre = models.ForeignKey(Genre, related_name='genres', on_delete=models.CASCADE, null=True)
    features = models.CharField(max_length=500, null=True, blank=True)
    song_file = models.FileField(upload_to='songs/%Y/%m/%d', blank=False, validators=[ExtensionValidator(['mp3', 'm4a']), validate_file_size])
    song_art = models.ImageField(upload_to='song_art/%Y/%m/%d', validators=[validate_image_size,])
    created = models.DateField(auto_now_add=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    play_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_songs', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=1, blank=True, null=True)
    is_draft = models.BooleanField(default=True)
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('song_name',)

    def __str__(self):
        return self.song_name

    def get_absolute_url(self):
        return reverse('muse:player',
                       args=[
                            self.id,
                            ])
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Contributions.objects.create(
                song=self,
                artist=self.artist,
                role='singer',
                percentage=100
            )

class Contributions(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_contributions')
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='artist_contributions')
    role = models.CharField(max_length=255, choices=[('writer', 'Writer'),
                                                     ('singer', 'Singer'),
                                                     ('producer', 'Producer'),
                                                     ('editor', 'Editor'),
                                                     ('director', 'Director'),
                                                     ('other', 'Other')], default='singer')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.artist.user} - {self.song.song_name}'
class Stream(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='streams')
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='song_streams', blank=True, null=True, default=None,
                             on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.song.song_name} streamed by {self.user.username}'

class Comments(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='comments', default=1)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.user} on {self.song}'

    objects = models.Manager()


def get_trending_songs():
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    trending_songs = cache.get('trending_songs')
    if trending_songs is None:
        trending_songs = Song.objects.annotate(stream_count=Count(
            'streams', filter=Q(streams__timestamp__gte=two_weeks_ago), is_draft=False)
        ).order_by('-stream_count')[:12]
        cache.set('trending_songs', trending_songs, 60)

    previous_trending_songs = cache.get('previous_trending_songs')

    for i, song in enumerate(trending_songs):
        if previous_trending_songs:
            previous_index = next((
                j for j, prev_song in enumerate(previous_trending_songs) if prev_song.id == song.id), None)
            if previous_index is not None:
                if i < previous_index:
                    song.movement = 'up'
                    song.movement_amount = previous_index - i
                elif i > previous_index:
                    song.movement = 'down'
                    song.movement_amount = i - previous_index
                else:
                    song.movement = 'same'
            else:
                song.movement = 'new'
        else:
            song.movement = 'new'
            cache.set('previous_trending_songs', trending_songs, 60 * 60*24)
    return trending_songs

def get_song_likes(song):
    return song.likes.count()

def get_user_likes(user):
    return user.liked_songs.all()

def recommend_songs(user):
    recommended_songs = cache.get(f'recommended_songs_{user.id}')
    if recommended_songs is None:
        liked_songs = get_user_likes(user)
        recommended_songs = Song.objects.filter(
            genre__in = [song.genre for song in liked_songs]).exclude(
            id__in=[song.id for song in liked_songs]).annotate(
            like_count=models.Count('likes'),
            streams_count = Count('play_count'),
            score=F('like_count') * 2 + F('streams_count')
        ).order_by('-score')[:10]
        cache.set(f'recommended_songs_{user.id}', recommended_songs, 60*60)
    return recommended_songs

def get_hot_artists():
    hot_artists = cache.get('hot_artists')
    if hot_artists is None:
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        hot_artists = ArtistProfile.objects.annotate(
            stream_count = Count('songs__streams', filter=models.Q(
                songs__streams__timestamp__gte=two_weeks_ago))
        ).annotate(
            total_activity= F('stream_count')
        ).order_by('-total_activity')[:10]
        cache.set('hot_artists', hot_artists, 60*60)
    return hot_artists

def get_new_songs():
    new_songs = cache.get('new_songs')
    if new_songs is None:
        month_ago = datetime.now() - timedelta(days=30)
        new_songs = Song.published.filter(created__gte = month_ago).annotate(
            likes_count = Count('likes'),
            streams_count = Count('play_count'),
            score=F('likes_count') * 2 + F('streams_count')
        ).order_by('-score')[:10]
        cache.set('new_songs', new_songs, 60*60)
    return new_songs


def get_popular_songs():
    popular_songs = cache.get('popular_songs')
    if popular_songs is None:
        popular_songs = Song.published.annotate(
            likes_count = Count('likes'),
            streams_count = Count('play_count'),
            score=F('likes_count') * 2 + F('streams_count')
        ).order_by('-score')[:10]
        cache.set('new_songs', popular_songs, 60*60)
    return popular_songs

def get_all_time_best_artists():
    all_time_best_artists = cache.get('all_time_best_artists')
    if all_time_best_artists is None:
        all_time_best_artists = ArtistProfile.objects.annotate(
            like_count=Count('songs__likes'),
            stream_count=Count('songs__streams')
        ).annotate(
            total_activity=F('like_count')+F('stream_count')
        ).order_by('-total_activity')[:10]
        cache.set('all_time_best_artists', all_time_best_artists, 60*60*24)
    return all_time_best_artists

def get_genre_songs():
    genres = cache.get('ingoma_songs')
    if genres is None:
        genres = Genre.objects.all()
        two_weeks_ago = datetime.now() - timedelta(days=30)
        subquery = Stream.objects.filter(
            song=OuterRef('pk'),
            timestamp__gte=two_weeks_ago
        ).order_by().values('song').annotate(growth=Count('id')).values('growth')
        songs_with_growth = Song.published.annotate(
            stream_growth=Subquery(subquery)
        ).order_by('-stream_growth')

        for genre in genres:
            genre.top_songs = songs_with_growth.filter(genre=genre)[:15]
        cache.set('ingoma_songs', genres, 60*60)
    return genres
class SiteData(models.Model):
    slug = models.SlugField(max_length=100, default='', unique=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=1)
    disk_image = models.ImageField(upload_to='disk_image/',blank=True)
    what_we_do = models.TextField(default='')
    why_work_with_us = models.TextField(default='')
    where_we_are = models.TextField(default='')

    class Meta:
        verbose_name = 'site_data'
        verbose_name_plural = 'site_data'
    objects = models.Manager()


class Promotions(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='promotions')
    body = models.TextField()
    created = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)
    slot = models.CharField(max_length=11,choices = [('slot 1', 'Slot 1'),
                                       ('slot 2', 'Slot 2'),
                                       ('slot 3', 'Slot 3')])
    def __str__(self):
        return f'{self.title} added to {self.slot}'

    class Meta:
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'