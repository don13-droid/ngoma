from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Genre, Song, Album,Stream, Promotions, get_new_songs, get_popular_songs,\
     Comments, SiteData, ArtistProfile, get_hot_artists, get_all_time_best_artists,\
    recommend_songs, get_trending_songs, get_genre_songs
from django.db.models import Count, Q,  OuterRef, Subquery, Sum
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserRegistrationForm, CommentForm, PayNowForm
from .forms import SearchForm
from .stream import STREAM
from django.contrib.auth.models import User
from django.core.cache import cache
from functools import wraps
import requests
import json
from django.contrib.auth.decorators import login_required

def cache_results(timeout=60*60):  # Default timeout is 1 hour
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            context ={
                'new_user':user_form
            }
            return render(request, 'admin_panel/register_done.html', context)
        else:
            print(user_form.errors)
            form = UserRegistrationForm()
            context = {
                'new_user':form
            }
            return render(request, 'admin_panel/register.html', context)
    else:
        user_form = UserRegistrationForm()
        context={
            'user_form':user_form
        }
        return render(request, 'admin_panel/register.html', context)


def artist_songs(artist):
    top_songs = Song.published.filter(artist=artist).annotate(total_streams=Sum('streams')) \
                    .order_by('-total_streams')
    return top_songs

@login_required
def increment_play_count(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            song_id = data.get('song_id')
            if not song_id:
                return JsonResponse({'message': 'Missing song_id'}, status=400)
            song = get_object_or_404(Song, id=song_id)
            stream = STREAM(request)
            stream.add(song=song, user=request.user)

            return JsonResponse({'message': 'Play Count Incremented'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'message': 'Error processing request'}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)




def paynowzw(amount, reference):
    integration_id = '14861'
    integration_key = 'da597709-1713-4404-af8d-6be150ce3b3c'

@login_required
def increment_song_likes(request):
    if request.method == 'POST':
        song_id = request.POST.get('song_id')
        song = get_object_or_404(Song,
                                 id = song_id)
        print(song.likes.all())
        if request.user in song.likes.all():
            song.likes.remove(request.user)
        else:
            song.likes.add(request.user)
    return JsonResponse({'status':'error'})

@login_required
def increment_comment_likes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment_id = data.get('comment_id')

            comment = get_object_or_404(Comments, id=comment_id)

            if request.user in comment.likes.all():
                comment.likes.remove(request.user)
            else:
                comment.likes.add(request.user)

            return JsonResponse({'likes': comment.likes.count()})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def play_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    songs_in_album = Song.published.filter(album=album)
    if request.user.is_authenticated:
        recommended_songs = recommend_songs(request.user)
    else:
        recommended_songs = []

    form = CommentForm()
    context = {
        'recommended_songs': recommended_songs,
        'songs': songs_in_album,
        'form': form,

    }
    return render(request, 'muse/play.html', context=context)


@require_POST
@login_required
def post_comment(request):
    song_id = request.POST.get('song_id')
    body = request.POST.get('body', '').strip()

    if not song_id or not body:
        return HttpResponseBadRequest()

    song = get_object_or_404(Song, id=song_id)
    comment = Comments.objects.create(
        song=song,
        user=request.user.profile,  # adjust for your user model
        body=body,
        active=True
    )
    comment.save()

    # return updated comment section
    comments = song.comments.filter(active=True, parent=None).prefetch_related('replies')
    html = render_to_string('muse/partials/comments.html', {'comments': comments, 'current_song': song}, request=request)
    return JsonResponse({'html': html})

@require_POST
@login_required
def post_reply(request):
    comment_id = request.POST.get('comment_id')
    body = request.POST.get('body', '').strip()

    if not comment_id or not body:
        return HttpResponseBadRequest()

    parent = get_object_or_404(Comments, id=comment_id)
    reply = Comments.objects.create(
        song=parent.song,
        user=request.user.profile,
        body=body,
        parent=parent,
        active=True
    )
    reply.save()

    # return updated comment section
    comments = parent.song.comments.filter(active=True, parent=None).prefetch_related('replies')
    html = render_to_string('muse/partials/comments.html', {'comments': comments, 'current_song': parent.song}, request=request)
    return JsonResponse({'html': html})

def get_comments(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    comments = song.comments.filter(active=True, parent=None).prefetch_related('replies')
    html = render_to_string('muse/partials/comments.html', {'comments': comments}, request=request)
    return JsonResponse({'html': html})
def play_song(request, song_id):
    song = get_object_or_404(Song,
                             id=song_id)
    if request.user.is_authenticated:
        recommended_songs = recommend_songs(request.user)
    else:
        recommended_songs = []
    top_songs = list(Song.published.filter(artist=song.artist))
    if song in top_songs:
        top_songs.remove(song)
    top_songs.insert(0, song)
    popular_songs = get_popular_songs()
    for song in popular_songs:
        top_songs.append(song)
    #recommended = Song.published.exclude(id__in=[s.id for s in top_songs])[:5]
    comments = song.comments.filter(active=True, parent=None).prefetch_related('replies')


    form = CommentForm()
    context = {
            'recommended_songs':recommended_songs,
            'songs':top_songs,
            'form':form,
            'comments': comments
        }
    return render(request, 'muse/play.html', context=context)


def home(request):
    top_songs = get_trending_songs()
    promotions = Promotions.objects.filter(active=True)
    if request.user.is_authenticated:
        recommended_songs = recommend_songs(request.user)
    else:
        recommended_songs = []
    top_artists = get_hot_artists()
    all_time_best = get_all_time_best_artists()
    popular_songs = get_popular_songs()
    new_songs = get_new_songs()
    context = {
        'promotions':promotions,
        'all_time_best':all_time_best,
        'top_artists':top_artists,
        'recommended_songs':recommended_songs,
        'top_songs':top_songs,
        'new_songs':new_songs,
        'popular_songs':popular_songs,
    }
    return render(request, 'muse/index.html', context)


def billboard(request):
    context = {
    }
    return render(request, 'muse/top_songs.html', context)


def artists(request):
    context = {

        }
    return render(request, 'muse/artists.html', context=context)



def single_album(request, pk):
    album = get_object_or_404(Album,
                                   id=pk)
    songs = Song.published.filter(album=album.id)
    artist = get_object_or_404(ArtistProfile, user=album.artist_id)
    other_songs = Song.published.filter(artist=artist).exclude(album=album.id)[:6]

    context = {
        'album': album,
        'songs': songs,
        'other_songs': other_songs
    }
    return render(request, 'muse/play-album.html', context)


def single_category(request, pk):
    category = get_object_or_404(Genre, id=pk)
    albums = Album.objects.filter(genre=category).order_by('-rating')[:12]
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_arg = cd['search']
            keywords = search_arg.split()
            query = Q()
            for keyword in keywords:
                query |= Q(song_name__icontains=keyword)
                query |= Q(artist__username__icontains=keyword)
                query |= Q(album__name__icontains=keyword)
                query |= Q(genre__name__icontains=keyword)

            object_list = Song.published.filter(query).distinct()
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
            form = SearchForm()
            if len(songs) != 0:
                header = f'Search results for "{search_arg}" in "{category.name}"'
            else:
                header = f'No Search results found for "{search_arg}" in "{category.name}"'
            context = {
                'header': header,
                'form': form,
                'category': category,
                'songs': songs,
                'albums': albums
            }
            return render(request, 'muse/single-category.html', context)
    else:
        last_week = timezone.now() - timedelta(days=14)
        object_list = Song.published.filter(genre=category)

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
        form = SearchForm()
        header = f'Top Songs In {category.name}'
        context = {
            'header':header,
            'form':form,
            'category': category,
            'songs': songs,
            'albums': albums
        }
        return render(request, 'muse/single-category.html', context)


def ingoma_songs(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_arg = cd['search']
            keywords = search_arg.split()
            query = Q()
            for keyword in keywords:
                query |= Q(song_name__icontains=keyword)
                query |= Q(artist__user__username__icontains=keyword)
                query |= Q(album__name__icontains=keyword)
                query |= Q(genre__name__icontains=keyword)
                query |= Q(features__icontains=keyword)

            songs = Song.published.filter(query).distinct()
            top_genres = Genre.objects.all()

            form = SearchForm()
            for genre in top_genres:
                genre.top_songs = songs.filter(genre=genre)
            if len(songs) != 0:
                header = f'Search results for "{search_arg}"'
            else:
                header = f'No Search results found for "{search_arg}"'
            context = {
                'header':header,
                'genres': top_genres,
                'form': form,
            }
            return render(request, 'muse/songs.html', context)
    else:
        top_genres = get_genre_songs()
        form=SearchForm()
        context={
            'genres':top_genres,
            'form':form,
            'header':'Ingoma Music'
        }
        return render(request,'muse/songs.html',context)


def ingoma_albums(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['search']
            keywords = name.split()
            query = Q()
            for keyword in keywords:
                query |= Q(name__icontains=keyword)
                query |= Q(artist__user__username__icontains=keyword)
                query |= Q(genre__name__icontains=keyword)

            object_list = Album.objects.filter(query)
            paginator = Paginator(object_list, 24)  # 3 posts in each page
            page = request.GET.get('page')
            try:
                albums = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer deliver the first page
                albums = paginator.page(1)
            except EmptyPage:
                # If page is out of range deliver last page of results
                albums = paginator.page(paginator.num_pages)
            form=SearchForm()
            if len(object_list) != 0:
                header = f'Search Results for "{name}"'
            else:
                header = f'No Search results found for "{name}"'
            context = {
                'header':header,
                'form':form,
                'albums':albums
            }
            return render(request,'muse/album.html', context)
    else:

        try:
            object_list = Album.objects.all().order_by('-rating')
        except:
            object_list = Album.objects.all()
        paginator = Paginator(object_list, 12)  # 3 posts in each page
        page = request.GET.get('page')
        try:
            albums = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            albums = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            albums = paginator.page(paginator.num_pages)

        form = SearchForm()
        header = 'Ingoma Albums'
        context={
            'header':header,
            'form':form,
            'albums':albums
        }
        return render(request,'muse/album.html',context)


def single_artist(request, pk):

    artist = get_object_or_404(ArtistProfile,
                                          id=pk)
    songs = Song.published.filter(artist=artist) \
                    .annotate(stream_count=Count('streams')) \
                    .order_by('-stream_count')
    top_songs = songs[:10]

    # Calculate the total streams for all songs of the artist
    total_streams = Stream.objects.filter(song__in=songs).count()
    total_songs = len(songs)

    context = {
        'artist':artist,
        'top_songs':top_songs,
        'total_songs':total_songs,
        'total_streams':total_streams

    }
    return render(request, 'muse/single_artist.html', context)


def newsletter(request):
    context = {

    }
    return render(request, 'muse/newsletter.html', context)
