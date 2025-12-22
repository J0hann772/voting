from django import forms

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


