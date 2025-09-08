"""
Forms for clients app.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SimpleUserCreationForm(forms.ModelForm):
    """Ultra-simple user creation form."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Laissez vide pour un mot de passe par défaut"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        help_texts = {
            'username': 'Nom d\'utilisateur unique',
            'email': 'Email (optionnel)',
            'first_name': 'Prénom (optionnel)',
            'last_name': 'Nom (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields.values():
            field.required = False
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_password('password123')  # Default password
        if commit:
            user.save()
        return user
