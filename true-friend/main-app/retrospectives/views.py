from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from core.constants import generation_app_url
import httpx
import datetime
# Create your views here.


class RetrospectiveView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    template_name = 'retrospectives/retrospectives.html'

    def get(self, request):
        url = f"{generation_app_url}/retrospective/{request.user.username}"
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

        # convert string datetime to real datetime object
        for element in response:
            element["date"] = datetime.datetime.fromisoformat(element["date"])

        context = {
            "retrospectives": response,
        }
        return render(request, self.template_name, context=context)

