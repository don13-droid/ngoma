from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Song, Album,Stream,\
    Events, Comments, SiteData, ArtistProfile
from django.db.models import Count, Q,  OuterRef, Subquery, Sum
from artist_admin.models import Sales
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserRegistrationForm, CommentForm, PayNowForm
from .forms import SearchForm
from paynow import Paynow
from .stream import STREAM
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth.models import User
from django.core.cache import cache
from functools import wraps


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
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            context ={
                'new_user':new_user
            }
            return render(request, 'admin_panel/register_done.html', context)
    else:
        user_form = UserRegistrationForm()
        context={
            'user_form':user_form
        }
    return render(request, 'admin_panel/register.html', context)


def buy_play(request, song_name, song_id):
    song = get_object_or_404(Song,
                             name=song_name,
                             id=song_id)
    if song.status == 'purchase':
        try:
            site_data = get_object_or_404(SiteData,
                                          slug='site-data')
            exchange_rate = site_data.exchange_rate
            price_in = exchange_rate * song.price
            price = round(price_in,2)
        except:
            price = 400 * song.price
    else:
        price = None
    comments = Comments.objects.filter(song=song.id, active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.song = song
            new_comment.save()
            comment_form = CommentForm()
            context = {
                'price':price,
                'comments': comments,
                'song': song,
                'new_comment': new_comment,
                'comment_form': comment_form
            }
            return render(request, 'muse/play.html', context)
    else:
        comment_form = CommentForm()
        context = {
            'price':price,
            'comments':comments,
            'song':song,
            'new_comment':new_comment,
            'comment_form':comment_form
        }
        return render(request,'muse/play.html',context)

def choose_purchase_opt(request, name, pk):
    song = get_object_or_404(Song,
                             name=name,
                             id=pk)
    context = {
        'song':song
    }
    return render(request, 'paynow/purchase_option.html',context)

def paynow_transfer(request, pk):
    song = get_object_or_404(Song,
                             id=pk)
    try:
        site_data = get_object_or_404(SiteData,
                                      slug='site-data')
        exchange_rate = site_data.exchange_rate
        price_in = exchange_rate * song.price
        price = round(price_in, 2)
    except:
        price = 400 * song.price
    integration_id = '14861'
    integration_key = 'da597709-1713-4404-af8d-6be150ce3b3c'
    if request.method == 'POST':
        form = PayNowForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            amount = cd['amount']
            email = cd['email']
            if amount < price:
                form = PayNowForm()
                header = f'Amount can not be less than {price}'
                context = {
                    'form': form,
                    'song': song,
                    'header': header
                }
                return render(request, 'paynow/paynow.html', context)
            else:
                paynow = Paynow(
                    integration_id,
                    integration_key,
                    'http://127.0.0.1:8000/muse/',
                    "https://google.com",
                )
                payment = paynow.create_payment('Order', email)
                payment.add(f'{song.id}', amount)
                response = paynow.send(payment)
                if response.success:
                    link = response.redirect_url
                    poll_url = response.poll_url
                    new_sale = Sales(song = song,
                                     user = request.user,
                                     artist = song.artist,
                                     email = email,
                                     poll_url = poll_url,
                                     amount = amount,
                                     status = 'pending'

                    ).save()
                    status = paynow.check_transaction_status(poll_url)
                    return redirect(link)
                else:
                    print('failed')
    form = PayNowForm()
    payment_type ='Transfer'
    header = f'{price}'
    context = {
        'header':header,
        'form':form,
        'payment_type':payment_type,
        'song':song
    }
    return render(request,'paynow/paynow.html', context)


def download_page(request,song_id, name):
    song = get_object_or_404(Song,
                             id=song_id,
                             name=name)
    context ={
        'song':song
    }
    return render(request,'muse/download_song.html',context)


def player(request, song, song_id):
    song = get_object_or_404(Song,
                             id=song_id,
                              slug=song)
    stream = STREAM(request)
    if request.user.is_authenticated:
        stream.add(song=song, user=request.user)
    else:
        stream.add(song=song, user=None)

    comment_form = CommentForm()


    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.song = song
            new_comment.user = request.user
            new_comment.save()


    else:
        comment_form = CommentForm()
    object_list = song.comments.filter(active=True)
    paginator = Paginator(object_list, 12)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        comments = paginator.page(paginator.num_pages)
    context = {
        'comments':comments,
        'form':comment_form,
        'song':song,
    }
    return render(request,'muse/player.html',context)

def all_categories(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_arg = cd['search']
            object_list = Category.objects.filter(name=search_arg)
            paginator = Paginator(object_list, 12)  # 3 posts in each page
            page = request.GET.get('page')
            try:
                categories = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer deliver the first page
                categories = paginator.page(1)
            except EmptyPage:
                # If page is out of range deliver last page of results
                categories = paginator.page(paginator.num_pages)
            form = SearchForm()
            if len(categories) != 0:
                header = f'Search results for "{search_arg}"'
            else:
                header = f'No Search results found for "{search_arg}"'
            context = {
                'header': header,
                'categories': categories,
                'form': form
            }
            return render(request, 'muse/categories.html', context)
    else:
        object_list = Category.objects.all()
        paginator = Paginator(object_list, 12)
        page = request.GET.get('page')
        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)
        form = SearchForm()
        header = 'All Categories'
        context = {
            'header':header,
            'form':form,
            'categories': categories,
        }
        return render(request, 'muse/categories.html', context)

# recomendations using AI
@cache_results(timeout=60*60)
def ai_recommendation(user_id):
    songs = Song.objects.all()
    songs_data = [{'song_id':song.id, 'song_name':song.name, 'genre':song.genre, 'rating':song.rating}
                 for song in songs]
    stream_counts = Stream.objects.values('user', 'song').annotate(stream_count=Count('id'))
    streams_data = [
        {'user_id': stream['user'], 'song_id':stream['song'], 'stream_count':stream['stream_count']}
        for stream in stream_counts
    ]
    #users_df = pd.DataFrame(users_data)
    songs_df = pd.DataFrame(songs_data)
    streams_df = pd.DataFrame(streams_data)
    songs_df['genre'] = songs_df['genre'].astype(str).str.lower()
    # Merge dataframes to get user-song-genre-rating-stream matrix
    user_song_matrix = pd.merge(streams_df, songs_df, on='song_id')[
        ['user_id', 'song_name', 'genre', 'rating', 'stream_count']]
    # Create a pivot table to get user-song matrix
    user_song_pivot = user_song_matrix.pivot(index='user_id', columns='song_name', values='stream_count').fillna(0)
    # Calculate the TF-IDF matrix for genres
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    genre_matrix = tfidf_vectorizer.fit_transform(songs_df['genre'])
    # Calculate cosine similarity between songs based on stream counts
    cosine_sim = cosine_similarity(user_song_pivot.T)

    num_recommendations = 10 
    user_songs = user_song_pivot.loc[user_id]
    similar_songs = []

    for song_name in user_songs.index:
        song_indices = songs_df[songs_df['song_name'] == song_name].index
        for song_idx in song_indices:
            if song_idx < len(cosine_sim):
                similar_songs.extend(list(enumerate(cosine_sim[song_idx])))

    similar_songs = sorted(similar_songs, key=lambda x: x[1], reverse=True)
    similar_songs = [song[0] for song in similar_songs if song[0] not in song_indices]

    recommendations = songs_df.iloc[similar_songs[:num_recommendations]]
    return recommendations

@cache_results(timeout=60*60)
def get_top_songs():
    last_week = timezone.now() - timedelta(days=7)
    top_songs = Song.objects.filter(streams__timestamp__gte=last_week) \
                    .annotate(total_streams=Sum('streams')) \
                    .order_by('-total_streams')
    return top_songs

@cache_results(timeout=60*60)
def newsongs():
    last_week = timezone.now() - timedelta(days=14)
    last_2_weeks = timezone.now() - timedelta(days=14)
    new_songs = Song.objects.filter(streams__timestamp__gte=last_week,created__gte=last_2_weeks) \
        .annotate(total_streams=Sum('streams')) \
        .order_by('-total_streams')
    return new_songs

@cache_results(timeout=60*60)
def get_albums():
    top_albums = Album.objects.filter(album_latest = True)
    return top_albums


@cache_results(timeout=60*60)
def top_artist(top_songs):
    popular_users = User.objects.filter(
        song__in=top_songs
    ).values_list('username', flat=True)[:12]

    id_list = list(popular_users.values('id').values_list('id', flat=True))
    # Retrieve artist profiles for these users
    popular_artist_profiles = ArtistProfile.objects.filter(
        user__in=id_list
    )
    return popular_artist_profiles


def home(request):
    try:
        top_songs = get_top_songs()[:10]
        best_song = get_object_or_404(Song,
                                      name=top_songs[0])
    except:
        top_songs = []
        best_song = []



    popular_artist_profiles = top_artist(top_songs)
    new_songs = newsongs()[:12]
    # song recommendations for logged on users
    if request.user.is_authenticated:
        try:
            recommendations = ai_recommendation(request.user.id)
            song_dict = dict(recommendations)
            recommended_songs = Song.objects.filter(id__in = list(song_dict['song_id']))
        except:
            recommended_songs = top_songs
    else:
        recommended_songs = top_songs

    top_albums = get_albums()
    context = {
        'top_artists':popular_artist_profiles,
        'recommended_songs':recommended_songs,
        'top_songs':top_songs[:10],
        'new_songs':new_songs,
        'top_albums':top_albums,
        'best_song':best_song
    }
    return render(request, 'muse/index.html', context)


def billboard(request):
    object_list = get_top_songs()[:100]
    paginator = Paginator(object_list, 25)  # 3 posts in each page
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
        'songs': songs
    }
    return render(request, 'muse/top_songs.html', context)


@cache_results(timeout=60*60)
def artists(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_arg = cd['search']
            keywords = search_arg.split()
            query = Q()
            for keyword in keywords:
                query |= Q(user__icontains=keyword)
                query |= Q(genre__icontains=keyword)
    else:
        top_songs = get_top_songs()[:10]
        popular_artist_profiles = top_artist(top_songs)
        form = SearchForm()
        context = {
            'top_artists':popular_artist_profiles,
            'form':form
        }
    return render(request, 'muse/artists.html', context=context)



def single_album(request, name, album):
    site_data = SiteData.objects.get(slug='site-data')
    album_name = get_object_or_404(Album,
                                   name=name,
                                   slug=album)
    songs = Song.objects.filter(album=album_name.id)
    other_songs = Song.objects.filter(artist=album_name.artist).exclude(album=album_name.id)[:6]
    context = {
        'site_data':site_data,
        'album': album_name,
        'songs': songs,
        'other_songs': other_songs
    }
    return render(request, 'muse/play-album.html', context)


def single_category(request, category):
    category = get_object_or_404(Category, slug=category)
    albums = Album.objects.filter(genre=category).order_by('-rating')[:12]
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_arg = cd['search']
            object_list = Song.objects.filter(name=search_arg, genre=category).annotate(
                                            total_plays=Count('plays')
                                                    ).order_by('-total_plays')
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
        object_list = Song.objects.filter(genre=category,
                                        streams__timestamp__gte=last_week) \
            .annotate(total_streams=Sum('streams')) \
            .order_by('-total_streams')

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

@cache_results(timeout=60*120)
def ingoma_songs(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            search_arg = cd['search']
            keywords = search_arg.split()
            query = Q()
            for keyword in keywords:
                query |= Q(name__icontains=keyword)
                query |= Q(artist__username__icontains=keyword)
                query |= Q(album__name__icontains=keyword)
                query |= Q(genre__name__icontains=keyword)
                query |= Q(features__username__icontains=keyword)

            object_list = Song.objects.filter(query, released='Released').distinct()
            paginator = Paginator(object_list, 24)  # 3 posts in each page
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
                header = f'Search results for "{search_arg}"'
            else:
                header = f'No Search results found for "{search_arg}"'
            context = {
                'header':header,
                'songs': songs,
                'form': form,
                'page':page
            }
            return render(request, 'muse/song_search.html', context)
    else:
        two_weeks_ago = timezone.now() - timedelta(weeks=2)
        subquery = Stream.objects.filter(
            song=OuterRef('pk'),
            timestamp__gte=two_weeks_ago
        ).order_by().values('song').annotate(growth=Count('id')).values('growth')
        songs_with_growth = Song.objects.annotate(
            stream_growth=Subquery(subquery)
        ).order_by('-stream_growth')
        top_genres = Category.objects.all()

        for genre in top_genres:
            genre.top_songs = songs_with_growth.filter(genre=genre)[:12]
        form=SearchForm()
        context={
            'genres':top_genres,
            'form':form
        }
        return render(request,'muse/songs.html',context)

@cache_results(timeout=60*120)
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
                query |= Q(artist__username__icontains=keyword)
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
                header = f'Showing Search Results for "{name}"'
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

def events(request):
    object_list = Events.objects.all()
    paginator = Paginator(object_list, 6)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        events = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        events = paginator.page(paginator.num_pages)
    context = {
        'events': events,
        'page': page
    }
    return render(request, 'muse/events.html', context)




def single_artist(request, pk):
    single_artist = get_object_or_404(ArtistProfile,
                                      user=pk)
    songs = Song.objects.filter(artist=single_artist.user.id) \
                    .annotate(stream_count=Count('streams')) \
                    .order_by('-stream_count')
    top_songs = songs[:10]

    # Calculate the total streams for all songs of the artist
    total_streams = Stream.objects.filter(song__in=songs).count()
    total_songs = len(songs)

    context = {
        'artist':single_artist,
        'top_songs':top_songs,
        'total_songs':total_songs,
        'total_streams':total_streams

    }
    return render(request, 'muse/single_artist.html', context)


def newsletter(request):
    context = {

    }
    return render(request, 'muse/newsletter.html', context)
