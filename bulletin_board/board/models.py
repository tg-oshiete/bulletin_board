from django.db import models
from django.contrib.auth.models import User


# class Profile(models.Model): # должен наследоваться от стандартного user
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     email_confirmed = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=100, unique = True)

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='ads_images/', blank=True, null=True)
    file = models.FileField(upload_to='ads_files/', blank=True, null=True) # сделать WYSIWYG-полем
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']


class Response(models.Model):
    text = models.TextField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'ad'] # один пользователь - один отклик на объявление