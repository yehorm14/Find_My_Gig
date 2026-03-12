from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from rango.models import Musician, Band

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class MusicianProfileForm(forms.ModelForm):
    class Meta:
        model = Musician
        fields = ['instruments', 'bio', 'profile_picture', 'media_link', 'location']

class BandProfileForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = ['name', 'location', 'bio', 'profile_picture']