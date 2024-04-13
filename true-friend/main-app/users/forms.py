from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.forms import ModelForm, FileInput
from django import forms
from .models import Profile, Notice
from .choices import GENDER_CHOICES, AGE_CHOICES
import logging

logger = logging.getLogger(__name__)
name_validator = RegexValidator(r'^[ㄱ-ㅎ가-힣][ㄱ-ㅎ가-힣]*[ㄱ-ㅎ가-힣]$', '한글만 입력가능합니다.')

class CustomUserAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        if username:
            # Convert username to lowercase
            self.cleaned_data['username'] = username.lower()
        return super().clean()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=200, strip=True, required=True, validators=[name_validator])
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    age = forms.ChoiceField(choices=AGE_CHOICES, required=True)

    class Meta:
        model = User # User, not Profile
        fields = ["username", "email", "password1", "password2", "name", "gender", "age"]
        labels = {
            "username": "Username",
            "email": "Email",
            "password1": "Password",
            "password2": "Confirm Password",
            "name": "Name",
            "gender": "Gender",
            "age": "Age",
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