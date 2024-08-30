from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import ValidationError,RegexValidator
from django.utils.translation import gettext_lazy as _
from mutagen import File
from mutagen.id3 import APIC

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

class Events(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    image = models.ImageField(upload_to='events_images')
    event_by = models.CharField(max_length=500)
    about_event = models.TextField()
    event_date = models.DateTimeField()
    event_venue =models.CharField(max_length=500)

    class Meta:
        ordering = ('event_date',)
        verbose_name = 'event'
        verbose_name_plural = 'events'

    def __str__(self):
        return self.name
    objects= models.Manager()

class Category(models.Model):
    name = models.CharField(max_length=500,
                        db_index=True)
    slug = models.SlugField(max_length=500,
                            unique=True)
    image = models.ImageField(upload_to='category_images', default='')
    about_category = models.TextField()

    def get_absolute_url(self):
        return reverse('muse:single_category',
                       args=[self.slug])

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    objects= models.Manager()

class ArtistProfile(models.Model):
    choices = (('male','Male'),('female','Female'))
    account_choices = (('basic','basic'),('premium','premium'),('platimum','platimum'))
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile-pictures', validators=[validate_image_size,], null=True)
    genre = models.ForeignKey(Category, related_name='genre_profiles', on_delete=models.CASCADE, default=1)
    phone = models.IntegerField(null=True, blank=True)
    bio = models.TextField(null= True, blank=True)
    sex = models.CharField(choices=choices, max_length=10)
    country = models.CharField(max_length=50, default='Zimbabwe')
    address = models.CharField(max_length=100, blank=True, null=True)
    user_account = models.CharField(max_length=50, choices=account_choices, default='basic')

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'Profiles'
    objects = models.Manager()

    def __str__(self):
        return str(self.user)

class Album(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500,
                            unique=True)
    genre = models.ForeignKey(Category, related_name='album_genre',
                                 on_delete=models.CASCADE, default='')
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    album_art = models.ImageField(upload_to='album_arts')
    about_album = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
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

class Song(models.Model):
    choices = (('free','free'),('purchase','purchase'))
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, default='')
    album = models.ForeignKey(Album,on_delete=models.CASCADE,blank=True, null= True, related_name='album_songs')
    genre = models.ForeignKey(Category, related_name='genres', on_delete=models.CASCADE)
    artist = models.ForeignKey(User,
                               on_delete=models.CASCADE, related_name='song'
                               )
    features = models.ManyToManyField(User, related_name='features' ,blank=True)
    song = models.FileField(upload_to='songs/%Y/%m/%d', blank=False, validators=[ExtensionValidator(['mp3', 'm4a']), validate_file_size])
    demo = models.FileField(upload_to='demos/%Y/%m/%d', blank=True, null=True, validators=[ExtensionValidator(['mp3', 'm4a']),validate_file_size])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, blank = True)
    song_art = models.ImageField(upload_to='song_art/%Y/%m/%d', validators=[validate_image_size,])
    song_bio = models.TextField(blank=True)
    status = models.CharField(choices=choices, max_length=50, default='free')
    created = models.DateTimeField(auto_now_add=True)
    released = models.CharField(max_length=20, choices=(('Released','Released'),('Draft','Draft')))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=1, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if self.song_art:
            try:
                # Get the path to the uploaded song file
                song_file_path = self.song.path
                print(song_file_path)

                # Open the song file using mutagen
                audio = File(song_file_path)

                # Add the song art to the song file
                if 'APIC:' in audio:
                    # If the song already has an art, remove it first
                    del audio['APIC:']
                audio.tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime='image/jpeg',  # Change to the appropriate MIME type
                        type=3,  # Front cover
                        desc='Cover',
                        data=self.song_art.read(),
                    )
                )

                # Save the modified song file
                audio.save()
            except Exception as e:
                print(f"Error adding artwork: {e}")


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    objects = models.Manager()

    def song_streams(self):
        streams = Stream.objects.filter(song=self.id).count()
        return streams

    def get_absolute_url(self):
        return reverse('muse:player',
                       args=[
                            self.id,
                            self.slug])

class Stream(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='streams')
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='userstreams', blank=True, null=True, default=None,
                             on_delete=models.CASCADE)

class Comments(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', default=1)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.user} on {self.song}'

    objects = models.Manager()



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


class OwnerShip(models.Model):
    song = models.ManyToManyField(Song, related_name='owner_song')
    artist = models.ManyToManyField(User, related_name='artist_share')
    share = models.DecimalField(decimal_places=2, max_digits=3)

    class Meta:
        verbose_name = 'Ownership'
        verbose_name_plural = 'Ownerships'

    def __str__(self):
        return 'song ownership updated'