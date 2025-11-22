from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm


def index(request):
    """Главная страница со статистикой"""
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='Запущена').count()
    unique_recipients = Recipient.objects.distinct().count()
    
    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }
    return render(request, 'mailings/index.html', context)


# CRUD для получателей (Recipients)
def recipient_list(request):
    """Список получателей"""
    recipients = Recipient.objects.all()
    return render(request, 'mailings/recipient_list.html', {'recipients': recipients})


def recipient_create(request):
    """Создание получателя"""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно создан!')
            return redirect('recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'mailings/recipient_form.html', {'form': form, 'title': 'Создать получателя'})


def recipient_update(request, pk):
    """Редактирование получателя"""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно обновлен!')
            return redirect('recipient_list')
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailings/recipient_form.html', {'form': form, 'title': 'Редактировать получателя'})


def recipient_delete(request, pk):
    """Удаление получателя"""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Получатель успешно удален!')
        return redirect('recipient_list')
    return render(request, 'mailings/recipient_confirm_delete.html', {'recipient': recipient})


# CRUD для сообщений (Messages)
def message_list(request):
    """Список сообщений"""
    messages_list = Message.objects.all()
    return render(request, 'mailings/message_list.html', {'messages_list': messages_list})


def message_create(request):
    """Создание сообщения"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно создано!')
            return redirect('message_list')
    else:
        form = MessageForm()
    return render(request, 'mailings/message_form.html', {'form': form, 'title': 'Создать сообщение'})


def message_update(request, pk):
    """Редактирование сообщения"""
    message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно обновлено!')
            return redirect('message_list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'mailings/message_form.html', {'form': form, 'title': 'Редактировать сообщение'})


def message_delete(request, pk):
    """Удаление сообщения"""
    message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Сообщение успешно удалено!')
        return redirect('message_list')
    return render(request, 'mailings/message_confirm_delete.html', {'message': message})


# CRUD для рассылок (Mailings)
def mailing_list(request):
    """Список рассылок"""
    mailings_list = Mailing.objects.all().prefetch_related('recipients', 'message')
    return render(request, 'mailings/mailing_list.html', {'mailings_list': mailings_list})


def mailing_create(request):
    """Создание рассылки"""
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно создана!')
            return redirect('mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailings/mailing_form.html', {'form': form, 'title': 'Создать рассылку'})


def mailing_update(request, pk):
    """Редактирование рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена!')
            return redirect('mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailings/mailing_form.html', {'form': form, 'title': 'Редактировать рассылку'})


def mailing_delete(request, pk):
    """Удаление рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена!')
        return redirect('mailing_list')
    return render(request, 'mailings/mailing_confirm_delete.html', {'mailing': mailing})


def mailing_detail(request, pk):
    """Детальная информация о рассылке"""
    mailing = get_object_or_404(Mailing, pk=pk)
    attempts = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_time')
    return render(request, 'mailings/mailing_detail.html', {
        'mailing': mailing,
        'attempts': attempts
    })


def send_mailing(request, pk):
    """Отправка рассылки вручную"""
    mailing = get_object_or_404(Mailing, pk=pk)
    
    if request.method == 'POST':
        recipients = mailing.recipients.all()
        success_count = 0
        fail_count = 0
        
        for recipient in recipients:
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=None,  # Используется DEFAULT_FROM_EMAIL из settings
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                # Создаем запись об успешной попытке
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status='Успешно',
                    server_response='Сообщение успешно отправлено'
                )
                success_count += 1
            except Exception as e:
                # Создаем запись о неуспешной попытке
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status='Не успешно',
                    server_response=str(e)
                )
                fail_count += 1
        
        # Обновляем статус рассылки
        if mailing.status == 'Создана':
            mailing.status = 'Запущена'
            mailing.save()
        
        messages.success(
            request, 
            f'Рассылка отправлена! Успешно: {success_count}, Неудачно: {fail_count}'
        )
        return redirect('mailing_detail', pk=mailing.pk)
    
    return render(request, 'mailings/mailing_send_confirm.html', {'mailing': mailing})
