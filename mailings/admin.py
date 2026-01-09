from django.contrib import admin
from .models import Recipient, Message, Mailing, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner', 'comment')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner', 'body')
    search_fields = ('subject', 'body')
    list_filter = ('owner',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'owner', 'status', 'start_time', 'end_time')
    list_filter = ('status', 'start_time', 'owner')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'recipient', 'status', 'attempt_time')
    list_filter = ('status', 'attempt_time')
    search_fields = ('mailing__message__subject', 'recipient__email')
    readonly_fields = ('attempt_time',)
