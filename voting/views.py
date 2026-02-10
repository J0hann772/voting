from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from voting.forms import CreateVotingForm, ReportForm, CommentForm, StatisticsForm
from voting.models import Choice, Vote, Voting, Report, Comment
from user.models import User
from django.contrib.admin.views.decorators import staff_member_required

def save_vote(request, voting_id: int):
    """
        Сохраняет голос текущего пользователя за выбранный вариант. ********!!

        Проверяет, не голосовал ли пользователь ранее, и если нет —
        создает запись голоса.

        Args:
            request (HttpRequest): Объект запроса Django.
            voting_id (int): Первичный ключ (ID) голосования.

        Returns:
            HttpResponseRedirect: Перенаправление на главную страницу после сохранения.

        Raises:
            Http404: Если голосование или вариант ответа не найдены.
        """

    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('main')

    choice_id = request.POST.get('choice_id')
    if not choice_id:
        messages.error(request, "Не выбран вариант для голосования")
        return redirect('voting', voting_id=voting_id)

    choice = get_object_or_404(Choice, id=choice_id)
    voting = choice.voting

    if not voting.is_active:
        messages.error(request, "Голосование завершено")
        return redirect('voting', voting_id=voting_id)

    existing_vote = Vote.objects.filter(
        author=request.user,
        choice__voting=voting
    ).exists()

    if existing_vote:
        messages.warning(request, "Вы уже проголосовали в этом опросе!")
        return redirect('voting', voting_id=voting_id)

    user_votes_count = Vote.objects.filter(
        author=request.user,
        choice__voting=voting
    ).count()

    if user_votes_count >= voting.max_votes:
        messages.warning(request, f"Вы не можете голосовать более {voting.max_votes} раз(а) в этом опросе!")
        return redirect('voting', voting_id=voting_id)

    # Создаем голос
    Vote.objects.create(
        author=request.user,
        choice=choice,
        created_at=timezone.now()
    )

    messages.success(request, "Ваш голос учтен!")
    return redirect('voting', voting_id=voting_id)


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
    page_val = request.GET.get('page')

    try:
        p_idx = int(page_val)
    except (TypeError, ValueError):
        p_idx = 1


    count = Voting.objects.count()

    pages_num = (count + 9) // 10


    start = (p_idx - 1) * 10
    end = p_idx * 10


    votings = Voting.objects.filter(visible=True)\
                        .prefetch_related('choices__votes', 'likes')\
                        .order_by('-id')[start:end]

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

@login_required
def report(request, voting_id):

    """
    Создание жалобы на голосование.

    Только для авторизованных пользователей. Позволяет оставить жалобу на голосование (можно либо выбрать готовую из списка, либо написать свою)

    Args:
        request (HttpRequest): Объект запроса Django.
        voting_id (int): Первичный ключ (ID) голосования.

    Returns:
        HttpResponse: HTML-страница с формой жалобы
    """

    title, description, error, report = None, None, None, None
    voting = get_object_or_404(Voting, id=voting_id)
    
    if request.method == "POST":
        report_form = ReportForm(request.POST)
        title = request.POST.get("title")
        description = request.POST.get("description", "")

        if report_form.is_valid():
            if not title:
                error = "Вы ничего не выбрали"
            elif title == "other" and not description:
                error = "Введите текст"
            else:
                report = Report(title = title, 
                                description = description,
                                author = request.user,
                                voting = voting)
                report.save()
                report_form = None

    else:
        report_form = ReportForm()

    context = {
        "report_form": report_form,
        "report_model": report,
        "error" : error
    }

    return render(request, "report.html", context)

@staff_member_required
def report_history(request):

    """
    Просмотр истории жалоб.

    Список всех жалоб в одной таблице. Доступно только staff.
    
    Args:
        request (HttpRequest): Объект запроса Django.

    Returns:
        HttpResponse: HTML-страница с таблицей всех жалоб
    """

    rep_history = Report.objects.all()
    context = {"rep_history" : rep_history}

    return render(request, "report_history.html", context)

@staff_member_required
def report_review(request, report_id):

    """
    Просмотр и рассмотрение конкретной жалобы.

    Доступно только staff. Позволяет забанить пользователя и/или удалить опрос и закрыть жалобу

    Args:
        request (HttpRequest): Объект запроса Django.
        report_id (int): Первичный ключ (ID) жалобы.

    Returns:
        HttpResponse: HTML-страница с возможностью рассмотреть жалобу
        HttpResponseRedirect: Перенаправление на страницу со всеми жалобами
        HttpResponseRedirect: Перенаправление на страницу с рассмотрением жалобы
    """


    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        if 'close_report' in request.POST:
            report.active = False
            report.save()
            return redirect('report_history')

        elif 'delete_voting' in request.POST:
            voting = report.voting
            voting.visible = False
            voting.save()
            return redirect('report_review', report_id=report.id)

        elif 'ban_user' in request.POST:
            user = report.voting.creator
            if not user.is_superuser:
                user.is_active = False
                user.save()
            return redirect('report_review', report_id=report.id)
        
    context = {'report': report}

    return render(request, 'report_review.html', context)

def voting(request, voting_id):

    """
    Просмотр страницы голосования.

    Отображается страница с конкретным голосованием, на которое нажал пользователь.

    Args:
        request (HttpRequest): Объект запроса Django.
        voting_id (int): Первичный ключ (ID) голосования.

    Returns:
        HttpResponse: HTML-страница с голосованием
        HttpResponseRedirect: Перенаправление на главную страницу
    """

    if request.method == 'POST':
        if 'delete_voting' in request.POST:
            v_id = request.POST.get('delete_voting')
            voting_to_delete = get_object_or_404(Voting, id=v_id)
            if voting_to_delete.creator == request.user:
                voting_to_delete.visible = False
                voting_to_delete.save()
                messages.success(request, "Голосование успешно удалено!")
                return redirect('main')
            else:
                messages.error(request, "Вы не можете удалить чужое голосование!")
                return redirect('voting', voting_id=voting_id)

    voting = get_object_or_404(Voting, id=voting_id)

    choices = voting.choices.all()
    total_votes = Vote.objects.filter(choice__voting=voting).count()

    choices_data = []
    for choice in choices:
        vote_count = choice.votes.count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0

        user_voted_for_this = False
        if request.user.is_authenticated:
            user_voted_for_this = Vote.objects.filter(
                author=request.user,
                choice=choice
            ).exists()

        choices_data.append({
            'choice': choice,
            'vote_count': vote_count,
            'percentage': round(percentage, 1),
            'user_voted': user_voted_for_this,
        })

    comments = voting.comments.filter(is_active=True).select_related('author', 'author__profile')

    if request.method == 'POST' and 'add_comment' in request.POST:
        if voting.commentaries and request.user.is_authenticated:
            comment_text = request.POST.get('comment_text', '').strip()
            if comment_text:
                if len(comment_text) < 5:
                    messages.error(request, "Комментарий должен содержать минимум 5 символов")
                elif len(comment_text) > 1000:
                    messages.error(request, "Комментарий не должен превышать 1000 символов")
                else:
                    Comment.objects.create(
                        voting=voting,
                        author=request.user,
                        text=comment_text
                    )
                    messages.success(request, "Ваш комментарий добавлен!")
                    return redirect('voting', voting_id=voting_id)

    user_voted = False
    if request.user.is_authenticated:
        user_voted = Vote.objects.filter(
            author=request.user,
            choice__voting=voting
        ).exists()

    context = {
        "v": voting,
        "choices_data": choices_data,
        "total_votes": total_votes,
        "user_voted": user_voted,
        "comments": comments,
        "comment_form": CommentForm() if voting.commentaries else None,
    }

    return render(request, "voting.html", context)


@staff_member_required
def statistics(request):
    form = StatisticsForm(request.GET or None)
    stats = None
    period_label = ""

    if form.is_valid():
        period = form.cleaned_data['period']
        now = datetime.now()

        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            period_label = "сегодня"
        elif period == 'yesterday':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end_date = start_date + timedelta(days=1)
            period_label = "вчера"
        elif period == 'week':
            start_date = now - timedelta(days=7)
            end_date = now
            period_label = "за последние 7 дней"
        elif period == 'month':
            start_date = now - timedelta(days=30)
            end_date = now
            period_label = "за последние 30 дней"
        else:  # custom
            start_date = datetime.combine(form.cleaned_data['start_date'], datetime.min.time())
            end_date = datetime.combine(form.cleaned_data['end_date'], datetime.max.time())
            period_label = f"с {start_date.date()} по {end_date.date()}"


        votings_in_period = Voting.objects.filter(
            created_at__range=[start_date, end_date],
            visible=True
        ).annotate(
            vote_count=Count('choices__votes', filter=Q(choices__votes__created_at__range=[start_date, end_date]))
        ).order_by('-vote_count')
        active_users = User.objects.filter(
            vote__created_at__range=[start_date, end_date]
        ).annotate(
            vote_count=Count('vote', filter=Q(vote__created_at__range=[start_date, end_date]))
        ).distinct().order_by('-vote_count')
        popular_choices = Choice.objects.filter(
            votes__created_at__range=[start_date, end_date]
        ).annotate(
            vote_count=Count('votes', filter=Q(votes__created_at__range=[start_date, end_date]))
        ).select_related('voting').order_by('-vote_count')[:10]
        total_votes = Vote.objects.filter(created_at__range=[start_date, end_date]).count()
        total_votings = votings_in_period.count()
        total_users = active_users.count()

        stats = {
            'period_label': period_label,
            'total_votes': total_votes,
            'total_votings': total_votings,
            'total_users': total_users,
            'votings_in_period': votings_in_period,
            'active_users': active_users,
            'popular_choices': popular_choices,
            'start_date': start_date,
            'end_date': end_date,
        }

    return render(request, 'statistics.html', {
        'form': form,
        'stats': stats,
    })