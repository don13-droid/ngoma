from django import forms
from django.contrib.auth.models import User
from .models import Comments, Song, Album, ArtistProfile, User
from django.forms import TextInput
from django.shortcuts import get_object_or_404

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_picture', 'address', 'phone', 'email', 'about_artist')

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = ('verification_status',)

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = ['artist','slug', 'rating', 'album_latest']

class ArtistAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_picture','phone', 'x',
                  'facebook', 'instagram', 'youtube')
class SearchForm(forms.Form):
    search = forms.CharField(label='Search',max_length=500)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            
        return user

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget = forms.Textarea(attrs = {'placeholder': 'post a comment.....'})

class SongUpload(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        super(SongUpload, self).__init__(*args, **kwargs)

        artist = ArtistProfile.objects.get(user=self.user)
        self.fields['album'].queryset = Album.objects.filter(artist=artist)
    class Meta:
        model = Song
        exclude = ['rating', 'artist', 'likes', 'play_count']

class PayNowForm(forms.Form):
    email = forms.EmailField()
    amount = forms.DecimalField(decimal_places=2)



