from django import forms
from django.contrib.auth.models import User
from .models import Comments, Song, Album, ArtistProfile
from django.forms import TextInput

class contract_form(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = '__all__'
class ProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = ['profile_picture','phone','sex']

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = ['artist','slug', 'rating', 'album_latest']

class ArtistAccountForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        exclude = ('user',)
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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)

class SongUpload(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        super(SongUpload, self).__init__(*args, **kwargs)

        self.fields['album'].queryset = Album.objects.filter(artist=self.user)
    class Meta:
        model = Song
        exclude = ['rating',]

class PayNowForm(forms.Form):
    email = forms.EmailField()
    amount = forms.DecimalField(decimal_places=2)



