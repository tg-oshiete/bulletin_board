from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Category, Ad, Response
from .forms import AdForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .forms import ResponseForm
from django.contrib.auth.models import User
from datetime import datetime, timedelta


def home_view(request):
    latest_ads = Ad.objects.filter(is_active=True).select_related(
        'author', 'category', 'author__profile'
    ).order_by('-created')[:6]
    categories = Category.objects.annotate(
        ad_count=Count('ad', filter=Q(ad__is_active=True))
    ).order_by('name')
    user_count = User.objects.count()
    ad_count = Ad.objects.filter(is_active=True).count()
    yesterday = datetime.now() - timedelta(days=1)
    response_count = Response.objects.filter(
        created_at__gte=yesterday
    ).count()
    context = {
        'latest_ads': latest_ads,
        'categories': categories,
        'user_count': user_count,
        'ad_count': ad_count,
        'response_count': response_count,
    }

    return render(request, 'index.html', context)


class AdListView(ListView):
    queryset =Ad.objects.all()
    template_name = 'ads/list.html'
    context_object_name = 'ads'
    paginate_by = 10
    ordering = ['-created']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = Response.objects.filter(ad=self.object)

        if self.request.user.is_authenticated:
            context['user_has_response'] = Response.objects.filter(
                ad=self.object,
                from_user=self.request.user
            ).exists()

        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    form_class = AdForm
    template_name = 'ads/create.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_hints'] = {
            'Танки': 'Защитники, щиты команды',
            'Хилы': 'Лекари, поддержка здоровья',
            'ДД': 'Урон, атакующие классы',
            'Торговцы': 'Продажа предметов, ремесло',
            'Гилдмастеры': 'Лидеры гильдий, организаторы',
            'Квестгиверы': 'Задания, миссии',
            'Кузнецы': 'Оружие, броня',
            'Кожевники': 'Кожаная броня, сумки',
            'Зельевары': 'Зелья, эликсиры',
            'Мастера заклинаний': 'Магия, заклинания'
        }
        return context


class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    fields = ['title', 'content', 'category', 'image', 'file', 'is_active']
    template_name = 'ads/create.html'
    success_url = reverse_lazy('ad_list')


class AdDeleteView(DeleteView):
    model = Ad


@login_required
def my_responses_view(request):
    user_ads = Ad.objects.filter(author=request.user)
    responses = Response.objects.filter(ad__in=user_ads).select_related('ad', 'from_user', 'ad__category').order_by('-created_at')
    filter_type = request.GET.get('filter', 'all')

    if filter_type == 'accepted':
        responses = responses.filter(is_accepted=True)
    elif filter_type == 'pending':
        responses = responses.filter(is_accepted=False)
    elif filter_type == 'my':
        responses = Response.objects.filter(from_user=request.user).select_related('ad', 'from_user', 'ad__category').order_by('-created_at')

    search_query = request.GET.get('search', '')
    if search_query:
        responses = responses.filter(
            Q(text__icontains=search_query) |
            Q(ad__title__icontains=search_query) |
            Q(from_user__username__icontains=search_query)
        )

    paginator = Paginator(responses, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_responses = Response.objects.filter(ad__in=user_ads).count()
    accepted_responses = Response.objects.filter(ad__in=user_ads, is_accepted=True).count()
    pending_responses = total_responses - accepted_responses

    context = {
        'page_obj': page_obj,
        'responses': page_obj.object_list,
        'total_responses': total_responses,
        'accepted_responses': accepted_responses,
        'pending_responses': pending_responses,
        'filter_type': filter_type,
        'search_query': search_query,
        'user_ads': user_ads,
    }

    return render(request, 'board/responses/list.html', context)


@login_required
def response_detail_view(request,pk):
    response = get_object_or_404(
        Response.objects.select_related('ad', 'from_user', 'ad__category'),
        pk=pk
    )
    if response.ad.author != request.user and response.from_user != request.user:
        messages.error(request, 'У вас нет прав для просмотра этого отклика')
        return redirect('my_responses')

    context = {
        'response': response,
        'is_owner': response.ad.author == request.user,
    }

    return render(request, 'board/responses/detail.html', context)

@login_required
def accept_response_view(request, pk):
    response = get_object_or_404(Response, pk=pk)

    if response.ad.author != request.user:
        messages.error(request, 'Вы не можете принимать отклики на чужие объявления')
        return redirect('my_responses')

    response.is_accepted = True
    response.save()

    messages.success(request, f'Отклик от {response.from_user.username} принят!')

    return redirect('my_responses')


@login_required
def delete_response_view(request, pk):
    response = get_object_or_404(Response, pk=pk)

    if response.ad.author != request.user and response.from_user != request.user:
        messages.error(request, 'У вас нет прав для удаления этого отклика')
        return redirect('my_responses')

    ad_title = response.ad.title

    if request.method == 'POST':
        response.delete()

        if response.ad.author == request.user:
            messages.success(request, f'Отклик на объявление "{ad_title}" удален')
        else:
            messages.success(request, f'Ваш отклик на объявление "{ad_title}" удален')

        return redirect('my_responses')

    context = {
        'response': response,
        'is_ad_owner': response.ad.author == request.user,
    }

    return render(request, 'board/responses/confirm_delete.html', context)



@login_required
def send_response_view(request, ad_pk):
    ad = get_object_or_404(Ad, pk=ad_pk)

    if ad.author == request.user:
        messages.error(request, 'Вы не можете оставлять отклики на свои объявления')
        return redirect('ad_detail', pk=ad.pk)

    if Response.objects.filter(ad=ad, from_user=request.user).exists():
        messages.error(request, 'Вы уже оставляли отклик на это объявление')
        return redirect('ad_detail', pk=ad.pk)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ad = ad
            response.from_user = request.user
            response.save()

            messages.success(request, 'Ваш отклик успешно отправлен!')


            return redirect('ad_detail', pk=ad.pk)
    else:
        form = ResponseForm()

    context = {
        'form': form,
        'ad': ad,
    }

    return render(request, 'board/responses/send.html', context)