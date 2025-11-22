from django.db import models


class Recipient(models.Model):
    """Модель получателя рассылки (клиента)"""
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['email']

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Модель сообщения для рассылки"""
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['subject']

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Модель рассылки"""
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана', verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатели')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-start_time']

    def __str__(self):
        return f"Рассылка {self.id} - {self.message.subject} ({self.status})"


class MailingAttempt(models.Model):
    """Модель попытки рассылки"""
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус')
    server_response = models.TextField(blank=True, verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, verbose_name='Получатель')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка {self.id} - {self.status} ({self.attempt_time})"
