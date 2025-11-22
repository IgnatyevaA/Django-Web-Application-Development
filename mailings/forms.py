from django import forms
from .models import Recipient, Message, Mailing


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'status', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        }

