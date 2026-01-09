from django.shortcuts import render, redirect, get_object_or_404

from voting.forms import CreateVotingForm
from voting.models import Choice, Vote, Voting


def save_vote(request, voting_id):
    if request.method != 'POST':
        return redirect('main')

    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    c_id = request.POST.get('choice_id')
    choice = get_object_or_404(Choice, id=c_id)
    voting = choice.voting


    user_votes = Vote.objects.filter(author=user, choice__voting=voting)


    if voting.voting_type == 'single' and user_votes.exists():
        return redirect('main')


    if voting.voting_type == 'multiple' and user_votes.count() >= voting.max_votes:
        return redirect('main')


    Vote.objects.get_or_create(author=user, choice=choice)

    return redirect('main')


def create_voting(request):
    if request.method != 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CreateVotingForm()
        context = {'form': form}

        return render(request, 'create_voting.html', context=context)

    form = CreateVotingForm(data=request.POST)

    if form.is_valid():
        voting = form.save(commit=False)


        voting.creator = request.user
        if voting.max_votes!=1:
            voting.voting_type = 'multiple'
        else:
            voting.voting_type = 'single'


        voting.save()
        return redirect('main')

    return redirect('main')


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

