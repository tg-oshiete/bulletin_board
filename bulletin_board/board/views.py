from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Category, Advertisement, Response


class AdvertisementListView(ListView):
    model = Advertisement


class AdvertisementDetailView(DetailView):
    model = Advertisement


class CreateAdvertisementView(LoginRequiredMixin, CreateView):
    model = Advertisement
    fields = ['title', 'content', 'category', 'image', 'file']
    template_name = 'board/ad_form.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateAdvertisementView(UpdateView):
    model = Advertisement
    fields = ['title', 'content', 'category', 'image', 'file', 'is_active']
    template_name = 'board/ad_form.html'


class DeleteAdvertisementView(DeleteView):
    model = Advertisement