from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gigs.models import Musician, Band

# ==========================================
# --- HELPER MIXINS ---
# ==========================================

class StyledFormMixin:
    """
    Mixin to automatically apply standard Bootstrap classes and 
    custom CSS variables to all form fields for UI consistency.
    """
    def apply_custom_styles(self):
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-2'
            field.widget.attrs['style'] = (
                'background-color: var(--card-bg, #2a2a35); '
                'color: #fff; '
                'border: 1px solid var(--border-dim, #444);'
            )


# ==========================================
# --- AUTHENTICATION FORMS ---
# ==========================================

class UserSignUpForm(StyledFormMixin, UserCreationForm):
    """
    Custom user registration form requiring an email address.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_custom_styles()
        
        # Add dynamic placeholders for the signup form specifically
        for field_name, field in self.fields.items():
            if field.label:
                field.widget.attrs['placeholder'] = f'Enter your {field.label.lower()}'


# ==========================================
# --- PROFILE MANAGEMENT FORMS ---
# ==========================================

class MusicianProfileForm(StyledFormMixin, forms.ModelForm):
    """Form for editing a Musician's profile details."""
    class Meta:
        model = Musician
        fields = ['instruments', 'bio', 'age', 'profile_picture', 'media_link', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_custom_styles()


class BandProfileForm(StyledFormMixin, forms.ModelForm):
    """Form for editing a Band or Venue's profile details."""
    class Meta:
        model = Band
        fields = ['name', 'location', 'bio', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_custom_styles()