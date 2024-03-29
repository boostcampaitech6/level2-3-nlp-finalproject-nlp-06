from django import forms
from .models import UserMessage, BotResponse


class UserMessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['message']
        widgets = {
            # choose html element (textarea) and apply custom css classes to the form fields
            'message': forms.Textarea(attrs={'id': 'user-input', 'class': 'user-input', 'placeholder': '메세지를 입력해주세요.', 'rows': '1', 'required': True}),
        }


class BotResponseForm(forms.ModelForm):
    class Meta:
        model = BotResponse
        fields = ['response']
