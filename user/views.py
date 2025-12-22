from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from user.forms import RegistrationForm


def index(request):
    return render(request, 'index.html')

def register_user(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')

    else:
        form = RegistrationForm()

    return render(request, 'registration/registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'login.html', context)



def logout_view(request):
    logout(request)
    return redirect('main')

