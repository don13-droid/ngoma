from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'muse'
urlpatterns=\
    [
        path('', views.home, name='dashboard'),
        path('artists/', views.artists, name='artists'),
        path('newsletter/', views.newsletter, name='newsletter'),
        path('billboard/', views.billboard, name='billboard'),
        path('ingoma_songs/', views.ingoma_songs, name='ingoma-songs'),
        path('ingoma_albums/', views.ingoma_albums, name='ingoma-albums'),
        path('increment_play_count/', views.increment_play_count, name='increment_play_count'),
        path('increment_song_like/', views.increment_song_likes, name='increment_song_likes'),
        path('increment_comment_like/', views.increment_comment_likes, name='increment_comment_likes'),
        path('register/', views.register, name='register'),
        path('login/', auth_views.LoginView.as_view(), name='login'),
        path(r'play/(<song_id>\w+)/',views.play_song,name='play-song'),
        path(r'play_album/(<album_id>\w+)', views.play_album, name='play_album'),
        path(r'single-artist/(<pk>\w+)/',views.single_artist, name='single-artist'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('password_change/', auth_views.PasswordChangeView.as_view(),name='password_change'),
        path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
        path(r'single-album/(<pk>\w+)/', views.single_album, name='single-album'),
        path(r'single-genre/(<pk>\w+)/', views.single_category, name='single_genre'),


]