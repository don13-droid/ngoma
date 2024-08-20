from . import views
from django.urls import path
app_name = 'artist_admin'

urlpatterns = [
    path('user_profile',views.user_profile, name='user-profile'),
    path('user_songs/', views.admin_songs, name='admin_songs'),
    path(r'update_albums/(<pk>\w+)/', views.album_update, name='update-album'),
    path('album-upload', views.add_album, name='add-album'),
    path('song-upload/', views.song_upload, name='song-upload'),
    path(r'delete-song/(<pk>\w+)/', views.delete_song, name='delete_song'),
    path(r'update-song/(<pk>\w+)/', views.update_song, name='update-song'),
    path(r'user_sales/(<id>\w+)/', views.user_sales, name='user_sales'),
    path(r'news-update/(<pk>\w+)/', views.updates_page, name='update-page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-albums', views.admin_albums, name='user-albums'),
]