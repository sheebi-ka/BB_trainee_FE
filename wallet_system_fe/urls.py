from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    
    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<str:member_id>/edit/', views.member_update, name='member_update'),
    path('members/<str:member_id>/delete/', views.member_delete, name='member_delete'),

    
    path('wallets/', views.wallet_list, name='wallet_list'),
    path('wallets/create/', views.wallet_create, name='wallet_create'),
    path('wallets/<str:member_id>/deposit/', views.wallet_deposit, name='wallet_deposit'),
    path('wallets/<str:member_id>/withdraw/', views.wallet_withdraw, name='wallet_withdraw'),

    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),

    
   
]
