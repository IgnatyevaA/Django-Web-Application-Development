from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Административная панель для пользователей"""
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone', 'country', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'phone', 'country')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'phone', 'country')
        }),
    )
    
    actions = ['block_users', 'unblock_users']
    
    def block_users(self, request, queryset):
        """Блокировка пользователей"""
        queryset.update(is_active=False)
        self.message_user(request, f'Заблокировано пользователей: {queryset.count()}')
    block_users.short_description = 'Заблокировать выбранных пользователей'
    
    def unblock_users(self, request, queryset):
        """Разблокировка пользователей"""
        queryset.update(is_active=True)
        self.message_user(request, f'Разблокировано пользователей: {queryset.count()}')
    unblock_users.short_description = 'Разблокировать выбранных пользователей'
