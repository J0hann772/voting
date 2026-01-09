import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):

    email = models.EmailField(max_length=40, unique=True, blank=False, null=False)
    nickname = models.CharField(max_length=40, blank=False, null=False, unique=True)

    USERNAME_FIELD = 'email' # вход по почте

    REQUIRED_FIELDS = ['username', 'nickname'] # для superuser

    def __str__(self):
        return self.username


def get_random_avatars():

    default_avatars = [
        'defaults/blue.svg',
        'defaults/red.svg',
        'defaults/green.svg'
        'defaults/yellow.svg',
        'defaults/pink.svg',
        'defaults/grey.svg'
    ]

    return random.choice(default_avatars)

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete= models.CASCADE)
    bio = models.TextField(blank=True)

    avatar = models.FileField(
        blank=True,
        upload_to='avatars/',
        default=get_random_avatars
    )


    def __str__(self):
        return f"Профиль {self.user.nickname}"

# профиль создается автоматически при регистрации пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)






