from django.shortcuts import redirect
from django.contrib import messages

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user_is_authenticated:
            messages.warning(request, 'Для доступа к этой странице необходимо войти в систему.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper