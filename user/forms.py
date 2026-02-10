from django import forms
from django.core.exceptions import ValidationError

from user.models import User


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_pass = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    class Meta:
        model = User
        fields = ['email', 'nickname', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Такой email уже зарегистрирован")
        return email

    def clean_nickname(self):
        name = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=name).exists():
            raise forms.ValidationError("Такое имя уже занято")
        return name


    def clean(self):
        data = super().clean()

        p1 = data.get('password')
        p2 = data.get('confirm_pass')


        if p1 and p2:
            if p1 != p2:

                self.add_error('confirm_pass', "Пароли не совпадают")

        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"]

        if commit:
            user.save()

        return user

class ChangeProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        target_field = kwargs.pop('target_field', None)
        super().__init__(*args, **kwargs)

        if target_field in self.fields:
            self.fields[target_field].required = True

    class Meta:
        model = User
        fields = ['email', 'nickname']

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Расскажите о себе...'}),
        label="О себе",
        required=False
    )


    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Старый пароль'}),
        label="Старый пароль",
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}),
        label="Новый пароль",
        required=False
    )
    confirm_pass = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите новый пароль'}),
        label="Повторите пароль",
        required=False
    )

    avatar = forms.ImageField(label="Аватар", required=False)


    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Такой email уже зарегистрирован")
        return email

    def clean_nickname(self):
        name = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Такое имя уже занято")
        return name

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:

            max_size = 2 * 1024 * 1024   # Ограничение 2 МБ
            if avatar.size > max_size:
                raise ValidationError("Файл слишком большой. Максимальный размер — 2 МБ.")
        return avatar


    def clean(self):

        user = self.instance
        data = super().clean()
        p_old = data.get('old_password')
        p1 = data.get('password')
        p2 = data.get('confirm_pass')
        if p_old and user:
            if not user.check_password(p_old):
                self.add_error('old_password', "Пароль неверный")

        if p1 and p_old and p_old == p1:
            self.add_error('password', "Новый пароль не должен совпадать со старым")

        if p1 and p2 and p1 != p2:
            self.add_error('password', "Пароли не совпадают")
            self.add_error('confirm_pass', "Пароли не совпадают")


        return data