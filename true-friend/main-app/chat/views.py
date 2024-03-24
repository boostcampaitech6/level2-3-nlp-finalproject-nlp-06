from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import httpx
from httpx import HTTPStatusError, RequestError
from asgiref.sync import sync_to_async

from core.constants import generation_app_url
from .forms import *
from .models import *



class ChatView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    template_name = 'chat/index.html'

    def get(self, request):
        bot_config = BotConfiguration.objects.first()
        bot_profile = bot_config.bot_profile
        user_message_form = UserMessageForm()
        profile = request.user.profile

        url = f"{generation_app_url}/sessions/{request.user.username}"
        try:
            response = httpx.get(url)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            response = []
        except Exception as e:
            print(f"An error occurred: {e}")
            response = []
        else:
            response = response.json()


        context = {
            'bot_profile': bot_profile,
            'profile': profile,
            'form': user_message_form,
            'turns': response,           
        }
        return render(request, self.template_name, context=context)
    

    def post(self, request):
        user_input = request.POST.get('message')

        url = f"{generation_app_url}/generate"
        data = {
            'username': request.user.username,
            'name': request.user.profile.name,
            'text': user_input
        }
        try:
            response = httpx.post(url, json=data, timeout=None)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            response = {"text": "", "personas": []}
        except Exception as e:
            print(f"An error occurred: {e}")
            response = {"text": "", "personas": []}
        else:
            response = response.json()

        context = {
            'response': response
        }
        return JsonResponse(context)




    




