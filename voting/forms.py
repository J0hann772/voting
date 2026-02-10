from django import forms
from datetime import datetime, timedelta
from voting.models import Report, Voting


class CreateVotingForm(forms.ModelForm):


    class Meta:
        model = Voting

        fields = ['title', 'description', 'max_votes', 'end_at', 'anonymous', 'commentaries']

        widgets = {
            'end_at': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class ReportForm(forms.Form):
    title = forms.ChoiceField(
        choices=Report.radio_report,
        widget=forms.RadioSelect,
        label="",
        required=True
    )
    description = forms.CharField(
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 2, "cols": 30}),
        label="",
        required=False,
    )


class StatisticsForm(forms.Form):
    PERIOD_CHOICES = [
        ('today', 'Сегодня'),
        ('yesterday', 'Вчера'),
        ('week', 'За неделю'),
        ('month', 'За месяц'),
        ('custom', 'Произвольный период'),
    ]

    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        widget=forms.RadioSelect,
        label="Выберите период",
        initial='week'
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Начальная дата",
        required=False
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Конечная дата",
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if period == 'custom':
            if not start_date:
                self.add_error('start_date', 'Укажите начальную дату для произвольного периода')
            if not end_date:
                self.add_error('end_date', 'Укажите конечную дату для произвольного периода')
            if start_date and end_date and start_date > end_date:
                self.add_error('start_date', 'Начальная дата не может быть позже конечной')

        return cleaned_data
class CommentForm(forms.Form):
    comment_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Оставьте ваш комментарий...',
            'maxlength': 1000,
        }),
        label="",
        max_length=1000,
        required=True
    )
    def clean_comment_text(self):
        text = self.cleaned_data.get('comment_text', '').strip()
        if len(text) < 5:
            raise forms.ValidationError("Комментарий должен содержать минимум 5 символов")
        return text