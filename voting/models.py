from django.db import models
from user.models import User


class Voting(models.Model): #Голосование

    class VotingType(models.TextChoices):
        SINGLE = 'single', 'Один вариант'
        MULTIPLE = 'multiple', 'Несколько вариантов'


    title = models.CharField(max_length=80)

    voting_type = models.CharField(
        max_length=10,
        choices=VotingType.choices,
        default=VotingType.SINGLE
    )

    max_votes = models.PositiveIntegerField(default=1, help_text="Максимум голосов от одного юзера")

    description = models.CharField(max_length=200, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name='liked_votings', blank=True)


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

    voting = models.ForeignKey(Voting, on_delete=models.CASCADE, related_name='reports')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=40, null=False, blank=False)
    description = models.CharField(max_length=300, null=False, blank=False)

    def __str__(self):
        return f"{self.author.username} оставил жалобу на {self.voting.title}"
















