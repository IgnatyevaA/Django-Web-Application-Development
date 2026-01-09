from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Номер телефона',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    country = forms.CharField(
        label='Страна',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'phone', 'country')


class UserLoginForm(AuthenticationForm):
    """Форма входа пользователя"""
    username = forms.CharField(
        label='Email',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Указываем, что поле username используется для поиска по email
        self.fields['username'].label = 'Email'

    def clean(self):
        """Переопределяем clean для корректной аутентификации по email"""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            from django.contrib.auth import authenticate
            from .models import User

            # Ищем пользователя по email
            try:
                user_obj = User.objects.get(email=username)
                # Аутентифицируем пользователя (Django использует USERNAME_FIELD)
                user = authenticate(
                    request=self.request,
                    username=user_obj.email,  # Передаем email как username
                    password=password
                )
                if user is None:
                    raise forms.ValidationError(
                        'Неверный email или пароль.',
                        code='invalid_login',
                    )
                self.confirm_login_allowed(user)
                # Сохраняем пользователя для использования в get_user()
                self.user_cache = user
            except User.DoesNotExist:
                raise forms.ValidationError(
                    'Неверный email или пароль.',
                    code='invalid_login',
                )

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'country', 'avatar')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
