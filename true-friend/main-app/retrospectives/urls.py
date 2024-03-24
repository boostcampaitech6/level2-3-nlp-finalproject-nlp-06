from django.urls import path
from . import views

urlpatterns = [
    path('', views.RetrospectiveView.as_view(), name='retrospectives'),
]