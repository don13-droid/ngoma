from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'muse'
urlpatterns=\
    [

        path('', views.home, name='category-list'),
        path('events/', views.events, name='events'),
        path('artists/', views.artists, name='artists'),
        path('newsletter/', views.newsletter, name='newsletter'),
        path('billboard/', views.billboard, name='billboard'),
        path('ingoma_songs/', views.ingoma_songs, name='ingoma-songs'),
        path('ingoma_albums/', views.ingoma_albums, name='ingoma-albums'),
        path('register/', views.register, name='register'),
        path('dashboard/', views.dashboard, name='dashboard'),
        path('song-upload/',views.song_upload, name='song-upload'),
        path('login/', auth_views.LoginView.as_view(), name='login'),
        path('user_songs/', views.admin_songs, name='admin_songs'),
        path(r'user_sales/(<id>\w+)/', views.user_sales, name='user_sales'),
        path('album-upload', views.add_album, name='add-album'),
        path('user-albums', views.admin_albums, name='user-albums'),
        path('user_profile',views.user_profile, name='user-profile'),
        path('contract', views.ingoma_contract, name='ingoma-contract'),
        path(r'news-update/(<pk>\w+)/',views.updates_page,name='update-page'),
        path('admin/order/<int:order_id>/', views.admin_order_detail,name='admin_order_detail'),
        path('all-categories/',views.all_categories, name='all-categories'),
        path(r'update_albums/(<pk>\w+)/', views.album_update, name='update-album'),
        path(r'play/(<song_name>\w+)/(<song_id>\w+)/',views.buy_play,name='buy-play'),
        path(r'download_song/(<id>\w+)/(<song_name>\w+)/',views.download_page,name='buy-play'),
        path(r'payment-opt/(<name>\w+)/(<pk>\w+)/',views.choose_purchase_opt,name='pay-opt'),
        path(r'paynow-transfer/(<pk>\w+)/',views.paynow_transfer,name='paynow-transfer'),
        path(r'update-song/(<pk>\w+)/',views.update_song,name='update-song'),
        path(r'delete-song/(<pk>\w+)/',views.delete_song,name='delete_song'),
        path(r'delete-album/(<pk>\w+)/',views.delete_album,name='delete_album'),
        path('<int:song_id>/<slug:song>/',views.player, name='player'),
        path(r'single-artist/(<pk>\w+)/',views.single_artist, name='single-artist'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout-dashboard'),
        path('<str:name>/<slug:album>/', views.single_album, name='single-album'),
        path('<slug:category>/', views.single_category, name='single_category'),

]