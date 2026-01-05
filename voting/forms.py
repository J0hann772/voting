from django import forms

from voting.models import Voting


class CreateVotingForm(forms.ModelForm):


    class Meta:
        model = Voting

        fields = ['title', 'description', 'max_votes']


