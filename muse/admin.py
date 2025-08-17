from django.contrib import admin
from .models import Genre, Song ,Album, Contributions,\
     Comments, SiteData, ArtistProfile, Stream,  User, Promotions
from django.urls import reverse
from django.utils.safestring import mark_safe


def order_detail(obj):
    url = reverse('muse:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


@admin.register(Promotions)
class PromotionsAdmin(admin.ModelAdmin):
    list_display = ['title', 'slot', 'created', 'active']
    list_filter = ['active']

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['song']
    list_filter = ['song']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'created','rating','genre','released', 'album_latest']
    list_filter = ['rating', 'created', 'genre','released']
    list_editable = ['album_latest','rating']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']

# Register your models here.
class ContributionAdmin(admin.TabularInline):
    model = Contributions
    extra = 1

class SongAdmin(admin.ModelAdmin):
    list_display = ['song_name','genre', 'artist','created','is_draft', 'play_count']
    list_filter = ['genre','is_draft', ]
    inlines = [ContributionAdmin]


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


class ArtistProfileInline(admin.StackedInline):
    model = ArtistProfile
    can_delete = False
    verbose_name_plural = 'Artist Profile'
    fk_name = 'user'

class CustomUserAdmin(admin.ModelAdmin):
    inlines = (ArtistProfileInline,)
    list_display = ('username', 'email', 'is_artist', 'is_staff')
    list_filter = ('is_artist', 'is_staff')

    def get_inline_instances(self, request, obj=None):
        if not obj or not obj.is_artist:
            return []
        return super().get_inline_instances(request, obj)

admin.site.register(User,CustomUserAdmin)
admin.site.register(Song, SongAdmin)