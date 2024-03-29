from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, FileInput
from django import forms
from .models import Profile, Notice


class CustomUserAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        if username:
            # Convert username to lowercase
            self.cleaned_data['username'] = username.lower()
        return super().clean()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User # User, not Profile
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Username",
            "email": "Email",
            "password1": "Password",
            "password2": "Confirm Password",
        }


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_image", "name"]
        labels = {
            "profile_image": "Profile Image",
            "name": "Name",
        }
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # No current file name and clear button for the profile_image field
        self.fields['profile_image'].widget = FileInput()

        # Set the input type of the profile_image field to file
        # self.fields['profile_image'].widget.attrs['onchange'] = 'previewImage();'


class NoticeForm(ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "text"]
        labels = {
            "title": "Title",
            "text": "Text",
        }
        widgets = {
            "text": forms.Textarea(attrs={"rows": 2}),
        }