import os

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404

from user.forms import RegistrationForm, ChangeProfileForm
from user.models import Profile, User


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

"""
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
"""


def logout_view(request):
    logout(request)
    return redirect('main')


def profile(request, nickname):

    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    found_profile = get_object_or_404(Profile, user__nickname=nickname)
    found_user = get_object_or_404(User, nickname=nickname)

    is_editing_mode = request.session.get('is_editing_mode', False)

    change_pair = ('', False)
    form = None

    if request.method == "POST":        # Если пользователь редактирует свой профиль, found_user == user

        act = request.POST.get("btn_action")
        mode = request.POST.get("edit_mode")
        can_edit = (user == found_user)

        if can_edit:

            if act == "start_editing":
                request.session['is_editing_mode'] = True
                return redirect('profile', nickname=nickname)
            elif act == "stop_editing":
                request.session['is_editing_mode'] = False
                return redirect('profile', nickname=nickname)

            if act == "save" :

                found_user = user
                form = ChangeProfileForm(request.POST, request.FILES, instance=user)

                if form.is_valid():

                    if 'avatar' in request.FILES:

                        if found_profile.avatar and not found_profile.avatar.name.startswith('defaults/'):
                            if os.path.isfile(found_profile.avatar.path):
                                os.remove(found_profile.avatar.path)


                        found_profile.avatar = request.FILES['avatar']
                        found_profile.save()

                    new_bio = form.cleaned_data.get('bio')
                    found_profile.bio = new_bio
                    found_profile.save()


                    new_p = form.cleaned_data.get('password')
                    if new_p:
                        user.set_password(new_p)
                        user.save()
                        update_session_auth_hash(request, user)
                    else:
                        form.save()

                    return redirect('profile', user.nickname)


                else:

                    change_pair = (f"changing_{mode}", True)





            elif act == "changing_nickname":
                change_pair = ('changing_nickname', True)

            elif act == "changing_email":
                change_pair = ('changing_email', True)

            elif act == "changing_bio":
                change_pair = ('changing_bio', True)

            elif act == "changing_password":
                change_pair = ('changing_password', True)

            elif act == "changing_avatar":
                change_pair = ('changing_avatar', True)

            elif act == "cansel_change":
                return redirect('profile', user.nickname)



            elif act == "cansel_change" :

                return redirect('profile', user.nickname)

    if form is None:
        form = ChangeProfileForm(instance=user, initial={'bio': found_profile.bio})

    ctx = {
        change_pair[0]: change_pair[1],
        'user': user,
        'found_profile': found_profile,
        'found_user': found_user,
        'is_editing_mode': is_editing_mode,
        'form': form
    }


    return render(request, 'profile.html', ctx)





