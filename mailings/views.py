from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from django.core.cache import cache
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm


def get_user_queryset(model, user):
    """Получить QuerySet с учетом прав доступа пользователя"""
    if not user.is_authenticated:
        return model.objects.none()
    if user.is_staff or user.groups.filter(name='Менеджеры').exists():
        return model.objects.all()
    return model.objects.filter(owner=user)


def index(request):
    """Главная страница со статистикой"""
    cache_key = 'index_stats'
    stats = cache.get(cache_key)

    if stats is None:
        total_mailings = Mailing.objects.count()
        now = timezone.now()
        # Активные рассылки - те, у которых текущая дата между start_time и end_time
        # Статус вычисляется динамически, поэтому проверяем только время
        active_mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now
        ).count()
        unique_recipients = Recipient.objects.distinct().count()

        stats = {
            'total_mailings': total_mailings,
            'active_mailings': active_mailings,
            'unique_recipients': unique_recipients,
        }
        cache.set(cache_key, stats, 300)  # Кеш на 5 минут

    return render(request, 'mailings/index.html', stats)


# CRUD для получателей (Recipients)
@login_required
def recipient_list(request):
    """Список получателей"""
    recipients = get_user_queryset(Recipient, request.user)
    return render(request, 'mailings/recipient_list.html', {'recipients': recipients})


@login_required
def recipient_create(request):
    """Создание получателя"""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user
            recipient.save()
            messages.success(request, 'Получатель успешно создан!')
            return redirect('mailings:recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'mailings/recipient_form.html', {'form': form, 'title': 'Создать получателя'})


@login_required
def recipient_update(request, pk):
    """Редактирование получателя"""
    recipient = get_object_or_404(get_user_queryset(Recipient, request.user), pk=pk)

    # Проверка прав: менеджеры могут только просматривать
    if request.user.groups.filter(name='Менеджеры').exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование.')
        return redirect('mailings:recipient_list')

    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно обновлен!')
            return redirect('mailings:recipient_list')
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailings/recipient_form.html', {'form': form, 'title': 'Редактировать получателя'})


@login_required
def recipient_delete(request, pk):
    """Удаление получателя"""
    recipient = get_object_or_404(get_user_queryset(Recipient, request.user), pk=pk)

    # Проверка прав: менеджеры могут только просматривать
    if request.user.groups.filter(name='Менеджеры').exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление.')
        return redirect('mailings:recipient_list')

    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Получатель успешно удален!')
        return redirect('mailings:recipient_list')
    return render(request, 'mailings/recipient_confirm_delete.html', {'recipient': recipient})


# CRUD для сообщений (Messages)
@login_required
def message_list(request):
    """Список сообщений"""
    messages_list = get_user_queryset(Message, request.user)
    return render(request, 'mailings/message_list.html', {'messages_list': messages_list})


@login_required
def message_create(request):
    """Создание сообщения"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            messages.success(request, 'Сообщение успешно создано!')
            return redirect('mailings:message_list')
    else:
        form = MessageForm()
    return render(request, 'mailings/message_form.html', {'form': form, 'title': 'Создать сообщение'})


@login_required
def message_update(request, pk):
    """Редактирование сообщения"""
    message = get_object_or_404(get_user_queryset(Message, request.user), pk=pk)

    # Проверка прав: менеджеры могут только просматривать
    if request.user.groups.filter(name='Менеджеры').exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование.')
        return redirect('mailings:message_list')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно обновлено!')
            return redirect('mailings:message_list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'mailings/message_form.html', {'form': form, 'title': 'Редактировать сообщение'})


@login_required
def message_delete(request, pk):
    """Удаление сообщения"""
    message = get_object_or_404(get_user_queryset(Message, request.user), pk=pk)

    # Проверка прав: менеджеры могут только просматривать
    if request.user.groups.filter(name='Менеджеры').exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление.')
        return redirect('mailings:message_list')

    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Сообщение успешно удалено!')
        return redirect('mailings:message_list')
    return render(request, 'mailings/message_confirm_delete.html', {'message': message})


# CRUD для рассылок (Mailings)
@login_required
def mailing_list(request):
    """Список рассылок"""
    mailings_list = get_user_queryset(Mailing, request.user).prefetch_related('recipients', 'message')
    # Обновляем статусы динамически
    for mailing in mailings_list:
        current_status = mailing.get_status()
        if mailing.status != current_status:
            mailing.status = current_status
            mailing.save(update_fields=['status'])
    return render(request, 'mailings/mailing_list.html', {'mailings_list': mailings_list})


@login_required
def mailing_create(request):
    """Создание рассылки"""
    if request.method == 'POST':
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.status = mailing.get_status()  # Устанавливаем статус динамически
            mailing.save()
            form.save_m2m()  # Сохраняем many-to-many связи
            messages.success(request, 'Рассылка успешно создана!')
            return redirect('mailings:mailing_list')
    else:
        form = MailingForm(user=request.user)
    return render(request, 'mailings/mailing_form.html', {'form': form, 'title': 'Создать рассылку'})


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки"""
    mailing = get_object_or_404(get_user_queryset(Mailing, request.user), pk=pk)

    # Проверка прав: менеджеры могут только просматривать
    if request.user.groups.filter(name='Менеджеры').exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование.')
        return redirect('mailings:mailing_list')

    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.status = mailing.get_status()  # Обновляем статус динамически
            mailing.save()
            form.save_m2m()
            messages.success(request, 'Рассылка успешно обновлена!')
            return redirect('mailings:mailing_list')
    else:
        form = MailingForm(instance=mailing, user=request.user)
    return render(request, 'mailings/mailing_form.html', {'form': form, 'title': 'Редактировать рассылку'})


@login_required
def mailing_delete(request, pk):
    """Удаление рассылки"""
    mailing = get_object_or_404(get_user_queryset(Mailing, request.user), pk=pk)

    # Проверка прав: менеджеры могут только просматривать
    if request.user.groups.filter(name='Менеджеры').exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление.')
        return redirect('mailings:mailing_list')

    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена!')
        return redirect('mailings:mailing_list')
    return render(request, 'mailings/mailing_confirm_delete.html', {'mailing': mailing})


@login_required
def mailing_detail(request, pk):
    """Детальная информация о рассылке"""
    mailing = get_object_or_404(get_user_queryset(Mailing, request.user), pk=pk)
    # Обновляем статус динамически
    current_status = mailing.get_status()
    if mailing.status != current_status:
        mailing.status = current_status
        mailing.save(update_fields=['status'])

    attempts = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_time')
    return render(request, 'mailings/mailing_detail.html', {
        'mailing': mailing,
        'attempts': attempts
    })


@login_required
def send_mailing(request, pk):
    """Отправка рассылки вручную"""
    mailing = get_object_or_404(get_user_queryset(Mailing, request.user), pk=pk)

    # Проверка времени рассылки
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        messages.error(
            request,
            f'Рассылка может быть отправлена только в период с {mailing.start_time} по {mailing.end_time}'
        )
        return redirect('mailings:mailing_detail', pk=mailing.pk)

    if request.method == 'POST':
        recipients = mailing.recipients.all()
        success_count = 0
        fail_count = 0

        for recipient in recipients:
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=None,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status='Успешно',
                    server_response='Сообщение успешно отправлено'
                )
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status='Не успешно',
                    server_response=str(e)
                )
                fail_count += 1

        # Обновляем статус рассылки
        mailing.status = mailing.get_status()
        mailing.save()

        messages.success(
            request,
            f'Рассылка отправлена! Успешно: {success_count}, Неудачно: {fail_count}'
        )
        return redirect('mailings:mailing_detail', pk=mailing.pk)

    return render(request, 'mailings/mailing_send_confirm.html', {'mailing': mailing})


@login_required
def attempt_list(request):
    """Список попыток рассылок"""
    if request.user.is_staff or request.user.groups.filter(name='Менеджеры').exists():
        attempts = MailingAttempt.objects.all().select_related('mailing', 'recipient')
    else:
        attempts = MailingAttempt.objects.filter(
            mailing__owner=request.user
        ).select_related('mailing', 'recipient')

    attempts = attempts.order_by('-attempt_time')
    return render(request, 'mailings/attempt_list.html', {'attempts': attempts})


@login_required
def statistics(request):
    """Статистика и отчеты по рассылкам пользователя"""
    if request.user.is_staff or request.user.groups.filter(name='Менеджеры').exists():
        mailings = Mailing.objects.all()
        attempts = MailingAttempt.objects.all()
    else:
        mailings = Mailing.objects.filter(owner=request.user)
        attempts = MailingAttempt.objects.filter(mailing__owner=request.user)

    # Статистика по рассылкам
    total_mailings = mailings.count()
    now = timezone.now()
    # Активные рассылки - те, у которых текущая дата между start_time и end_time
    active_mailings = mailings.filter(
        start_time__lte=now,
        end_time__gte=now
    ).count()
    # Завершенные рассылки - те, у которых end_time в прошлом
    completed_mailings = mailings.filter(end_time__lt=now).count()

    # Статистика по попыткам
    total_attempts = attempts.count()
    successful_attempts = attempts.filter(status='Успешно').count()
    failed_attempts = attempts.filter(status='Не успешно').count()

    # Статистика по сообщениям
    total_messages_sent = successful_attempts

    # Детальная статистика по каждой рассылке
    mailing_stats = []
    for mailing in mailings:
        mailing_attempts = attempts.filter(mailing=mailing)
        mailing_stats.append({
            'mailing': mailing,
            'total_attempts': mailing_attempts.count(),
            'successful': mailing_attempts.filter(status='Успешно').count(),
            'failed': mailing_attempts.filter(status='Не успешно').count(),
        })

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'completed_mailings': completed_mailings,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'failed_attempts': failed_attempts,
        'total_messages_sent': total_messages_sent,
        'mailing_stats': mailing_stats,
    }

    return render(request, 'mailings/statistics.html', context)
