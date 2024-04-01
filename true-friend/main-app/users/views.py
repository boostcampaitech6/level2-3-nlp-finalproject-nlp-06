from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Profile, Notice
from .forms import CustomUserAuthenticationForm, CustomUserCreationForm, ProfileForm, NoticeForm
import json
# Create your views here.

class LoginUserView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    form_class = CustomUserAuthenticationForm
    
    def get_success_url(self):
        return reverse_lazy('index') 
    
    def get_redirect_url(self) -> str:
        return super().get_redirect_url()
     
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username').lower()
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request,'Invalid username or password')
            return super().form_invalid(form)
    

class RegisterUserView(View):
    template_name = 'users/register.html'

    def get(self, request):
        form = CustomUserCreationForm()
        if request.user.is_authenticated:
            return redirect('index')
        
        context = {'form': form}
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('username').lower()
            user.save()

            profile = Profile.objects.create(user=user)
            profile.name = form.cleaned_data.get('name')
            profile.gender = form.cleaned_data.get('gender')
            profile.age = form.cleaned_data.get('age')
            profile.save()
            messages.success(request, 'Account created successfully')
            login(request, user)
            return redirect('user-profile')
        else:
            messages.error(request, 'Error creating account')
            context = {'form': form}
            return render(request, self.template_name, context=context)
    

class UserProfileView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    template_name = 'users/user-profile.html'
    
    def get(self, request):
        profile = request.user.profile
        form = ProfileForm(instance=profile)
        context = {'profile': profile, 'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request):
        profile = request.user.profile # get the profile of the logged in user
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('user-profile')
        else:
            messages.error(request, 'Error updating profile')
            context = {'profile': profile, 'form': form}
            return render(request, self.template_name, context=context)
    

class DeleteAccountView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    model = User
    template_name = 'users/delete-account.html'
    success_url = reverse_lazy('login')

    # bypasses the need for a pk in the URL, as we are deleting the currently logged-in user
    def get_object(self, queryset=None):
        # Return the currently logged-in user; no need for a pk in the URL
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Account deleted successfully')
        return redirect(self.get_success_url())


class NoticeView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    template_name = 'users/notices.html'
    
    def get(self, request):
        profile = request.user.profile
        notices = profile.notices.filter(is_read=False)
        print(notices)
        form = NoticeForm()
        context = {'notices': notices, 'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request):
        profile = request.user.profile
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.receiver = profile 
            notice.save()
            messages.success(request, 'Notice saved successfully')
            return redirect('notice')
        else:
            messages.error(request, 'Error saving notice')
            context = {'notices': profile.notices.all(), 'form': form}
            return render(request, self.template_name, context=context)

    def delete(self, request):
        try:
            # Decode request.body and convert from JSON string to Python dictionary
            data = json.loads(request.body.decode('utf-8'))
            notice_id = data.get('notice_id')
            print(f"Notice ID: {notice_id}")
            # Ensure notice_id is not None and is a valid integer
            if notice_id:
                notice = get_object_or_404(Notice, id=notice_id)
                notice.delete()
                return JsonResponse({'message': 'Notice deleted successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Notice ID not provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


