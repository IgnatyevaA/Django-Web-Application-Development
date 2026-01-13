from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Mailing, Message, Recipient


class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" с соответствующими правами'

    def handle(self, *args, **options):
        # Создаем или получаем группу
        group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Менеджеры" уже существует'))

        # Получаем ContentType для моделей
        mailing_ct = ContentType.objects.get_for_model(Mailing)
        message_ct = ContentType.objects.get_for_model(Message)
        recipient_ct = ContentType.objects.get_for_model(Recipient)

        # Добавляем права на просмотр всех рассылок, сообщений и получателей
        permissions = [
            Permission.objects.get_or_create(
                codename='can_view_all_mailings',
                name='Может просматривать все рассылки',
                content_type=mailing_ct
            )[0],
            Permission.objects.get_or_create(
                codename='can_view_all_messages',
                name='Может просматривать все сообщения',
                content_type=message_ct
            )[0],
            Permission.objects.get_or_create(
                codename='can_view_all_recipients',
                name='Может просматривать всех получателей',
                content_type=recipient_ct
            )[0],
            Permission.objects.get_or_create(
                codename='can_disable_mailing',
                name='Может отключать рассылки',
                content_type=mailing_ct
            )[0],
        ]
        
        # Добавляем права в группу
        for permission in permissions:
            group.permissions.add(permission)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Группе "Менеджеры" добавлены права: {len(permissions)}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'Группа "Менеджеры" успешно настроена!'
            )
        )
