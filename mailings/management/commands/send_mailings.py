from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from mailings.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Отправка рассылок по расписанию'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Получаем рассылки, которые нужно отправить
        mailings = Mailing.objects.filter(
            status__in=['Создана', 'Запущена'],
            start_time__lte=now,
            end_time__gte=now
        )
        
        for mailing in mailings:
            self.stdout.write(f'Обработка рассылки #{mailing.id}: {mailing.message.subject}')
            
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
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Отправлено: {recipient.email}')
                    )
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        recipient=recipient,
                        status='Не успешно',
                        server_response=str(e)
                    )
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Ошибка для {recipient.email}: {str(e)}')
                    )
            
            # Обновляем статус рассылки
            if mailing.status == 'Создана':
                mailing.status = 'Запущена'
                mailing.save()
            
            # Проверяем, не закончилось ли время рассылки
            if now >= mailing.end_time:
                mailing.status = 'Завершена'
                mailing.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Рассылка #{mailing.id} завершена. Успешно: {success_count}, Неудачно: {fail_count}'
                )
            )
        
        # Обновляем статусы завершенных рассылок
        completed_mailings = Mailing.objects.filter(
            status='Запущена',
            end_time__lt=now
        )
        count = completed_mailings.update(status='Завершена')
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Обновлено статусов завершенных рассылок: {count}')
            )

