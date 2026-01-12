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

    class Meta:
        unique_together = ['author', 'choice']

    def __str__(self):
        return f"{self.author.username} проголосовал за {self.choice.text}"


class Report(models.Model):

    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, related_name='Жалобы')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=40, null=False, blank=False)
    description = models.CharField(max_length=300, null=False, blank=False)

    def __str__(self):
        return f"{self.author.username} оставил жалобу на {self.voting.title}"
















