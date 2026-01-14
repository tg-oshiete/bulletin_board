from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from board.models import Ad, Response
from django.conf import settings
from .forms import (UserForm, ProfileForm, CustomUserCreationForm, CustomAuthenticationForm,
                    PasswordResetRequestForm, SetNewPasswordForm)
from django.core.mail import send_mail
import uuid


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    user_ads = Ad.objects.filter(author=user)
    user_responses = Response.objects.filter(from_user=user)
    profile.total_ads = user_ads.count()
    profile.total_responses = user_responses.count()
    profile.save()

    context = {
        'profile': profile,
        'user_ads': user_ads.order_by('-created')[:5],
        'user_responses': user_responses.order_by('-created_at')[:5],
        'recent_activity': get_recent_activity(user),
    }

    return render(request, 'account/profile.html', context)


def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    user_ads = Ad.objects.filter(author=user, is_active=True)
    context = {
        'profile_user': user,
        'profile': profile,
        'user_ads': user_ads.order_by('-created')[:10],
        'total_ads': user_ads.count(),
        'is_owner': request.user == user,
    }
    return render(request, 'account/public_profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'account/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def profile_settings(request):
    return render(request, 'account/profile_settings.html', {
        'profile': request.user.profile
    })


def get_recent_activity(user):
    activity = []

    recent_ads = Ad.objects.filter(author=user).order_by('-created')[:3]
    for ad in recent_ads:
        activity.append({
            'type': 'ad',
            'object': ad,
            'time': ad.created,
            'message': f'Создал объявление "{ad.title}"'
        })

    recent_responses = Response.objects.filter(from_user=user).order_by('-created_at')[:3]
    for response in recent_responses:
        activity.append({
            'type': 'response',
            'object': response,
            'time': response.created_at,
            'message': f'Оставил отклик на "{response.ad.title}"'
        })

    activity.sort(key=lambda x: x['time'], reverse=True)
    return activity[:10]


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            send_welcome_email(user)
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'account/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            profile = user.profile
            profile.save()
            messages.success(request, f'Добро пожаловать, {user.username}!')

            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()

    return render(request, 'account/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')


def send_welcome_email(user):
    subject = 'Добро пожаловать на MMORPG Форум!'
    message = f'''
    Приветствуем, {user.username}!

    Спасибо за регистрацию на нашем форуме.

    Теперь вы можете:
    - Создавать объявления
    - Оставлять отклики
    - Общаться с другими игроками
    - Настроить свой профиль

    Приятного использования!

    С уважением,
    Команда MMORPG Форума
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)

                token = str(uuid.uuid4())
                user.profile.password_reset_token = token
                user.profile.save()

                reset_link = request.build_absolute_uri(
                    f'/account/password-reset/{user.id}/{token}/'
                )

                send_mail(
                    'Сброс пароля - MMORPG Форум',
                    f'Для сброса пароля перейдите по ссылке: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Инструкции по сбросу пароля отправлены на ваш email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'account/auth/password_reset.html', {'form': form})


def password_reset_confirm(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if user.profile.password_reset_token != token:
            messages.error(request, 'Неверная или устаревшая ссылка.')
            return redirect('login')

        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                password1 = form.cleaned_data['new_password1']
                password2 = form.cleaned_data['new_password2']

                if password1 != password2:
                    messages.error(request, 'Пароли не совпадают.')
                else:
                    user.set_password(password1)
                    user.save()

                    user.profile.password_reset_token = ''
                    user.profile.save()

                    messages.success(request, 'Пароль успешно изменен.')
                    return redirect('login')
        else:
            form = SetNewPasswordForm()

        return render(request, 'account/auth/password_reset_confirm.html', {'form': form})

    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('login')