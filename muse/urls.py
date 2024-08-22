from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'muse'
urlpatterns=\
    [
        path('', views.home, name='dashboard'),
        path('events/', views.events, name='events'),
        path('artists/', views.artists, name='artists'),
        path('newsletter/', views.newsletter, name='newsletter'),
        path('billboard/', views.billboard, name='billboard'),
        path('ingoma_songs/', views.ingoma_songs, name='ingoma-songs'),
        path('ingoma_albums/', views.ingoma_albums, name='ingoma-albums'),
        path('register/', views.register, name='register'),
        path('login/', auth_views.LoginView.as_view(), name='login'),
        path('all-categories/',views.all_categories, name='all-categories'),
        path(r'play/(<song_name>\w+)/(<song_id>\w+)/',views.buy_play,name='buy-play'),
        path(r'download_song/(<id>\w+)/(<song_name>\w+)/',views.download_page,name='buy-play'),
        path(r'payment-opt/(<name>\w+)/(<pk>\w+)/',views.choose_purchase_opt,name='pay-opt'),
        path(r'paynow-transfer/(<pk>\w+)/',views.paynow_transfer,name='paynow-transfer'),
        path('<int:song_id>/<slug:song>/',views.player, name='player'),
        path(r'single-artist/(<pk>\w+)/',views.single_artist, name='single-artist'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('<str:name>/<slug:album>/', views.single_album, name='single-album'),
        path('<slug:category>/', views.single_category, name='single_category'),
]