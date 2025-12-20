from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):

    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=40, blank=True, null=True)

    USERNAME_FIELD = 'email' # вход по почте

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete= models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

# профиль создается автоматически при регистрации пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)






