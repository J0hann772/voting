from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from user.models import User


def get_end_time():
    return timezone.now() + timedelta(days=7)

class Voting(models.Model): #Голосование



    """class VotingType(models.TextChoices):
        SINGLE = 'single', 'Один вариант'
        MULTIPLE = 'multiple', 'Несколько вариантов'"""

    """voting_type = models.CharField(
        max_length=10,
        choices=VotingType.choices,
        default=VotingType.SINGLE
    )"""



    max_votes = models.PositiveIntegerField(default=1, verbose_name="Максимум голосов от одного пользователя")
    num_choices = models.PositiveIntegerField(default=2, verbose_name="Количество вариантов голоса")

    title = models.CharField(max_length=80, verbose_name='Заголовок')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Описание')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False, verbose_name="Анонимное голосование")
    end_at = models.DateTimeField(default=get_end_time, help_text='Время по МСК')
    created_at = models.DateTimeField(auto_now_add=True)
    commentaries = models.BooleanField(default=True, verbose_name="Коментарии")
    is_active = models.BooleanField(default=True, verbose_name="Статус")
    visible = models.BooleanField(default=True, verbose_name="Видимость")

    likes = models.ManyToManyField(User, related_name='liked_votings', blank=True)

    def clean(self):

        start_time = self.created_at or timezone.now()
        if self.end_at and start_time >= self.end_at:
            raise ValidationError({'end_at': 'Дата окончания должна быть позже даты создания'})

        if self.max_votes > self.num_choices:
            raise ValidationError({'max_votes': 'Голосов не может быть больше, чем самих вариантов.'})


class Choice(models.Model): #Вариант голоса

    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300, null=False, blank=False)


class Vote(models.Model): #Голос

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['author', 'choice']

    def __str__(self):
        return f"{self.author.username} проголосовал за {self.choice.text}"


class Report(models.Model):
    radio_report = [
    ("rights", "Нарушены авторские права"),
    ("fake", "Ложная информация"),
    ("unpleasant", "Неприятный контент"),
    ("offended", "Это меня оскорбило"),
    ("other", "Другое")]

    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, related_name='Reports')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=40, null=False, blank=False, choices=radio_report)
    description = models.CharField(max_length=300, null=False, blank=True) #поставила blank - True, чтобы при radio было пустое описание
    active = models.BooleanField(default=1)

    def __str__(self):
        return f"{self.author.nickname} оставил жалобу на {self.voting.title}"

class Comment(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий от {self.author.nickname} к {self.voting.title}"