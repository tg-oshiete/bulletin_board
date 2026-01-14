from django.urls import path
from .views import AdCreateView, AdListView, AdUpdateView, AdDetailView, AdDeleteView
from . import views

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('create/', AdCreateView.as_view(), name='ad_create'),
    path('<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('<int:pk>/delete', AdDeleteView.as_view(), name='ad_delete'),
    path('responses/', views.my_responses_view, name='my_responses'),
    path('responses/<int:pk>/', views.response_detail_view, name='response_detail'),
    path('responses/<int:pk>/accept/', views.accept_response_view, name='accept_response'),
    path('responses/<int:pk>/delete/', views.delete_response_view, name='delete_response'),
    path('ad/<int:ad_pk>/send-response/', views.send_response_view, name='send_response'),
]