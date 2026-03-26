from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gigs.models import Musician, Band

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-2'
            field.widget.attrs['style'] = 'background-color: var(--card-bg, #2a2a35); color: #fff; border: 1px solid var(--border-dim, #444);'
            field.widget.attrs['placeholder'] = f'Enter your {field.label.lower()}'

class MusicianProfileForm(forms.ModelForm):
    class Meta:
        model = Musician
        fields = ['instruments', 'bio', 'age', 'profile_picture', 'media_link', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-2'
            field.widget.attrs['style'] = 'background-color: var(--card-bg, #2a2a35); color: #fff; border: 1px solid var(--border-dim, #444);'

class BandProfileForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = ['name', 'location', 'bio', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-2'
            field.widget.attrs['style'] = 'background-color: var(--card-bg, #2a2a35); color: #fff; border: 1px solid var(--border-dim, #444);'