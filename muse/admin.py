from django.contrib import admin
from .models import Category, Song ,Album,\
    Events, Comments, SiteData, ArtistProfile, Stream,  OwnerShip
from django.urls import reverse
from django.utils.safestring import mark_safe


def order_detail(obj):
    url = reverse('muse:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')






@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['song']
    list_filter = ['song']

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ['name','image','event_by','event_date']
    list_filter = ['event_date']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'created','rating','genre', 'album_latest']
    list_filter = ['name', 'artist','rating', 'created', 'genre']
    list_editable = ['album_latest','rating']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug','image', 'about_category']
    list_filter = ['name']
    prepopulated_fields = {'slug': ('name',)}

# Register your models here.
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['name','slug','genre', 'artist','created']
    list_filter = ['artist','genre', 'created','album']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['user','created','active']
    list_filter = ['created','active']



def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')

@admin.register(SiteData)
class SiteDataAdmin(admin.ModelAdmin):
    list_display = ['slug','exchange_rate']

@admin.register(ArtistProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','phone','sex']
    list_filter = ['user','sex']