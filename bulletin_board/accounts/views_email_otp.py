from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import secrets
from .views import send_welcome_email


def send_otp_email(email, token):
    subject = 'Код подтверждения регистрации - MMORPG Форум'

    message = f'''
    Ваш код подтверждения для регистрации: {token}

    Код действителен 10 минут.

    Введите этот код на сайте для завершения регистрации.

    Если вы не регистрировались, проигнорируйте это письмо.

    С уважением,
    Команда MMORPG Форума
    '''

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"DEBUG: OTP отправлен на {email}: {token}")  # Для отладки
    except Exception as e:
        print(f"DEBUG: Ошибка отправки email: {e}")
        # Для тестирования - выводим код в консоль
        print(f"DEBUG: Код для {email}: {token}")


def register_step1(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not email or '@' not in email:
            messages.error(request, 'Введите корректный email')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
        elif not username or len(username) < 3:
            messages.error(request, 'Имя пользователя должно быть не менее 3 символов')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        elif not password1 or len(password1) < 8:
            messages.error(request, 'Пароль должен быть не менее 8 символов')
        elif password1 != password2:
            messages.error(request, 'Пароли не совпадают')
        else:
            token = ''.join(secrets.choice('0123456789') for _ in range(6))

            request.session['register_data'] = {
                'email': email,
                'username': username,
                'password': password1,
                'otp': token,
                'otp_time': timezone.now().isoformat(),
            }

            send_otp_email(email, token)

            messages.success(request, f'Код подтверждения отправлен на {email}')
            return redirect('register_code')

    return render(request, 'account/auth/email_register_step1.html')


def register_step2(request):
    if request.user.is_authenticated:
        return redirect('profile')

    register_data = request.session.get('register_data')

    if not register_data:
        messages.error(request, 'Сессия устарела. Начните регистрацию заново.')
        return redirect('register')

    email = register_data.get('email')
    stored_token = register_data.get('otp')
    token_time = register_data.get('otp_time')

    if token_time:
        token_time = timezone.datetime.fromisoformat(token_time)
        if timezone.now() - token_time > timezone.timedelta(minutes=10):
            messages.error(request, 'Код устарел. Запросите новый.')
            request.session.pop('register_data', None)
            return redirect('register')

    if request.method == 'POST':
        if 'resend_code' in request.POST:
            new_token = ''.join(secrets.choice('0123456789') for _ in range(6))

            register_data['otp'] = new_token
            register_data['otp_time'] = timezone.now().isoformat()
            request.session['register_data'] = register_data

            send_otp_email(email, new_token)

            messages.success(request, 'Новый код отправлен!')
            return redirect('register_code')

        entered_token = request.POST.get('token', '').strip()

        if len(entered_token) != 6 or not entered_token.isdigit():
            messages.error(request, 'Введите 6-значный цифровой код')
        elif entered_token != stored_token:
            messages.error(request, 'Неверный код')
        else:
            username = register_data['username']
            password = register_data['password']

            try:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Пользователь с таким email уже существует')
                    request.session.pop('register_data', None)
                    return redirect('register')

                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Пользователь с таким именем уже существует')
                    return redirect('register_code')

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True
                )
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                request.session.pop('register_data', None)
                messages.success(request, f'Регистрация завершена! Добро пожаловать, {username}!')
                send_welcome_email(user)
                return redirect('profile')

            except Exception as e:
                print(f"DEBUG: Ошибка создания пользователя: {e}")
                messages.error(request, 'Ошибка при создании аккаунта')

    return render(request, 'account/auth/email_register_step2.html', {'email': email})


def register_finalize(request):
    return redirect('register_code')