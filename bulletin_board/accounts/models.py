from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    website = models.URLField(blank=True, verbose_name='Веб-сайт')
    discord = models.CharField(max_length=50, blank=True, verbose_name='Discord')
    steam = models.CharField(max_length=50, blank=True, verbose_name='Steam ID')
    total_ads = models.PositiveIntegerField(default=0, verbose_name='Всего объявлений')
    total_responses = models.PositiveIntegerField(default=0, verbose_name='Всего откликов')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')
    email_notifications = models.BooleanField(default=True, verbose_name='Уведомления по email')
    password_reset_token = models.CharField(max_length=100, blank=True, verbose_name='Токен сброса пароля')


    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()