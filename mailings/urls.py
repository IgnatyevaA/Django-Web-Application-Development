from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    
    # Получатели
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/create/', views.recipient_create, name='recipient_create'),
    path('recipients/<int:pk>/update/', views.recipient_update, name='recipient_update'),
    path('recipients/<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),
    
    # Сообщения
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/update/', views.message_update, name='message_update'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    
    # Рассылки
    path('mailings/', views.mailing_list, name='mailing_list'),
    path('mailings/create/', views.mailing_create, name='mailing_create'),
    path('mailings/<int:pk>/', views.mailing_detail, name='mailing_detail'),
    path('mailings/<int:pk>/update/', views.mailing_update, name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.mailing_delete, name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.send_mailing, name='send_mailing'),
    
    # Попытки и статистика
    path('attempts/', views.attempt_list, name='attempt_list'),
    path('statistics/', views.statistics, name='statistics'),
    
    # Детальные страницы
    path('recipients/<int:pk>/', views.recipient_detail, name='recipient_detail'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    
    # Отключение рассылки (для менеджеров)
    path('mailings/<int:pk>/disable/', views.mailing_disable, name='mailing_disable'),
]

