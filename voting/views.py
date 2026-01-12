from django.shortcuts import render, redirect, get_object_or_404

from voting.forms import CreateVotingForm
from voting.models import Choice, Vote, Voting


def save_vote(request, voting_id):
    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('main')

    c_id = request.POST.get('choice_id')
    ans = get_object_or_404(Choice, id=c_id)
    v_obj = ans.voting


    user_votes = Vote.objects.filter(author=request.user, choice__voting=v_obj)
    if user_votes.count() >= v_obj.max_votes:
        return redirect('main')

    Vote.objects.get_or_create(author=request.user, choice=ans)
    return redirect('main')

def create_voting(request):
    if not request.user.is_authenticated:
        return redirect('login')

    opts = ['', '']
    msg = None

    if request.method == 'POST':
        form = CreateVotingForm(request.POST)
        opts = request.POST.getlist('choice_text')
        btn = request.POST.get('action')

        if btn == 'add_choice':

            has_empty = False
            for x in opts:
                if not x.strip():
                    has_empty = True
                    break

            if has_empty:
                msg = "Нельзя добавить новое поле, пока есть пустые варианты!"
            else:
                opts.append('')

        elif btn and btn.startswith('remove_'):

            idx = int(btn.split('_')[1])
            if len(opts) > 2:
                opts.pop(idx)
            else:
                msg = "Нельзя оставить меньше двух вариантов!"


        elif btn == 'save_voting':

            valid_opts = [t.strip() for t in opts if t.strip()]


            form.instance.num_choices = len(valid_opts)

            if form.is_valid():
                mv = form.cleaned_data.get('max_votes')
                nc = len(valid_opts)

                if nc < 2:
                    msg = "Нужно заполнить хотя бы два варианта!"
                elif mv >= nc:
                    msg = f"Голосов ({mv}) должно быть меньше выбора ({nc})!"
                else:
                    obj = form.save(commit=False)
                    obj.creator = request.user
                    obj.num_choices = nc
                    obj.save()

                    for text in valid_opts:
                        Choice.objects.create(voting=obj, text=text)

                    return redirect('main')
    else:
        form = CreateVotingForm()

    return render(request, 'create_voting.html', {
        'form': form,
        'choices': opts,
        'error': msg
    })

def index(request):
    if request.method == 'POST':
        if 'delete_voting' in request.POST:
            v_id = request.POST.get('delete_voting')


            Voting.objects.filter(id=v_id).delete()


            return redirect('main')


    page_val = request.GET.get('page')


    try:
        p_idx = int(page_val)
    except (TypeError, ValueError):
        p_idx = 1


    count = Voting.objects.count()

    pages_num = (count + 9) // 10


    start = (p_idx - 1) * 10
    end = p_idx * 10


    votings = Voting.objects.prefetch_related('choices__votes', 'likes').all()[start:end]

    ctx = {
        'votings': votings,
        'pages': range(1, pages_num + 1),

        'current_page': p_idx
    }

    if request.user.is_authenticated:
        ctx['user'] = request.user

    ctx = {
        'votings': votings,
        'pages': range(1, pages_num + 1),

        'current_page': p_idx
    }

    return render(request, 'index.html', ctx)

