from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Sales
from .models import News_and_Updates
from django.utils import timezone
import datetime
from django.db.models import Count, Sum
from datetime import timedelta
from muse.models import ArtistProfile, Song, Album, Stream
from muse.forms import  ProfileForm, AlbumForm, SongUpload, ArtistAccountForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
@login_required
def user_profile(request):
    try:
        profile = get_object_or_404(ArtistProfile,
                                    user=request.user.id)
    except:
        profile = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_data= form.save(commit=True)
            form = ProfileForm(instance=profile)
            context ={
                'profile':profile,
                'form':form
            }
            return render(request,'admin_panel/profile.html',context)

    else:
        form = ProfileForm(instance=profile)
        context = {
            'form':form,
            'profile':profile
        }
        return render(request,'artist_admin/profile.html', context)

@login_required
def admin_songs(request):
    object_list = Song.objects.filter(artist=request.user.id)
    paginator = Paginator(object_list, 12)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        songs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        songs = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        songs = paginator.page(paginator.num_pages)
    context = {
        'songs':songs
    }
    return render(request,'artist_admin/admin_songs.html',context)

@login_required
def album_update(request, pk):
    instance = get_object_or_404(Album,
                                 id=pk)
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.save()
            header = 'Album successfully changed'
            form = SongUpload(instance=instance)
            context = {
                'header': header,
                'form': form
            }
            return render(request, 'artist_admin/add_album.html', context)
    else:
        form = AlbumForm(instance=instance)
        header = 'Edit Album'
        context = {
            'header': header,
            'form': form
        }
        return render(request, 'artist_admin/add_album.html', context)

@login_required
def add_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['name']
            new_album = form.save(commit=False)
            new_album.artist = request.user
            new_album.save()
            header = f'Album "{name}" successfully added'
            form = AlbumForm()

    form = AlbumForm()
    header = 'Upload Album'
    context = {
        'form':form
    }
    return render(request,'artist_admin/add_album.html',context)

@login_required
def update_song(request, pk):
    instance = get_object_or_404(Song,
                                 id=pk)
    if request.method == 'POST':
        form = SongUpload(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.save()
            header = 'Song successfully changed'
            form= SongUpload(instance=instance)
            context ={
                'header':header,
                'form':form
            }
            return render(request, 'artist_admin/song_upload.html', context)
    else:
        form = SongUpload(instance=instance)
        header = 'Edit Song'
        context ={
            'header':header,
            'form':form
        }
        return render(request,'artist_admin/song_upload.html',context)

@login_required
def delete_song(request, pk):
    song  = get_object_or_404(Song,
                              id=pk)
    song.delete()
    objects = 'Song'
    context = {
        'object':objects,
        'song':song
    }
    return render(request,'artist_admin/info_page.html', context)

@login_required
def song_upload(request):
    if request.method == 'POST':
        data = get_object_or_404(ArtistProfile,
                                 user=request.user.id)
        form = SongUpload(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data

            objects = form.save(commit=False)
            objects.artist = request.user
            objects.save()
            form = SongUpload()
            song_name = cd['name']
            header = f'Song "{song_name}" uploaded successfully'
            context = {
                'header': header,
                'form': form
            }
            return render(request, 'artist_admin/song_upload.html', context)
        else:
            print(form.errors)

    else:
        form = SongUpload(user=request.user)
        header = 'Song Details'
    context ={
            'header':header,
            'form':form
        }
    return render(request, 'artist_admin/song_upload.html',context)



@login_required
def admin_albums(request):
    Albums = Album.objects.filter(artist=request.user.id)
    context = {
        'albums':Albums
    }
    return render(request,'artist_admin/admin_albums.html',context)



def artist_monthly_revenue(artist):

    current_month = datetime.datetime.now().month
    sales = Sales.objects.filter(artist=artist,
                                 created__month=current_month)
    artist_revenue = sum(transaction.amount for transaction in sales)
    return artist_revenue

def payable_revenue(artist):
    sales = Sales.objects.filter(artist=artist,
                                 cleared= False)
    total_sales = sum(amount.amount for amount in sales)
    return total_sales
def artist_total_streams(artist):
    songs = Song.objects.filter(artist=artist)
    # Calculate the total streams for all songs of the artist
    total_streams = Stream.objects.filter(song__in=songs).count()
    return total_streams

def best_perfoming_songs(artist):
    last_week = timezone.now() - timedelta(days=7)
    top_songs = Song.objects.filter(artist=artist,
                                    streams__timestamp__gte=last_week) \
        .annotate(total_streams=Sum('streams')) \
        .order_by('-total_streams')[:10]
    return top_songs

def recent_sales(artist):
    sales = Sales.objects.filter(artist=artist).order_by('-created')[:10]
    return sales

def recent_updates():
    updates = News_and_Updates.objects.filter(status='published').order_by('-created')
    return updates[:10]
@login_required
def dashboard(request):

    monthly_revenue = artist_monthly_revenue(request.user.id)
    sales_recent = recent_sales(request.user.id)
    total_streams = artist_total_streams(request.user.id)
    total_comments = Song.objects.filter(artist=request.user.id).aggregate(Count('comments'))
    pr = payable_revenue(request.user.id)
    top_songs = best_perfoming_songs(request.user.id)

    updates = recent_updates()
    context={
        'total_comments':total_comments['comments__count'],
        'total_streams':total_streams,
        'payable_revenue':pr,
        'top_songs':top_songs,
        'sales':sales_recent,
        'updates':updates,
        'monthly_revenue':monthly_revenue
    }
    return render(request, 'artist_admin/index.html',context)

@login_required
def updates_page(request, pk):
    update = get_object_or_404(News_and_Updates,
                               id=pk)
    context = {
        'update':update
    }
    return render(request, 'artist_admin/news_updates.html', context = context)

@login_required
def user_sales(request, id):
    object_list = Sales.objects.filter(artist = id)
    paginator = Paginator(object_list, 12)
    page = request.GET.get('page')
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)

    pr = payable_revenue(request.user.id)
    monthly_revenue = artist_monthly_revenue(request.user.id)
    context = {
        'payable_revenue':pr,
        'monthly_revenue':monthly_revenue,
        'sales':sales,
        'page':page

    }

    return render(request, 'artist_admin/sales_list.html',context)

def create_artist_account(request):
    if request.method == 'POST':
        form = ArtistAccountForm(request.POST, request.FILES)
        if form.is_valid():
            new_artist = form.save(commit=False)
            new_artist.user = request.user
            new_artist.save()
            return render(request, 'artist_admin/index.html')
        else:
            print(form.errors)



    else:
        form = ArtistAccountForm()
        context = {
            'form':form
        }
        return render(request, 'artist_admin/create_artist_account.html', context)
