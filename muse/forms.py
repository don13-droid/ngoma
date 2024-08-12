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
        fields = ['name','genre','artist','album_art','about_album']

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
        fields = ('name', 'email', 'body')

class SongUpload(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['name','album','genre',
                  'features','song',
                  'price','song_art','song_bio','status','released']

class PayNowForm(forms.Form):
    email = forms.EmailField()
    amount = forms.DecimalField(decimal_places=2)



