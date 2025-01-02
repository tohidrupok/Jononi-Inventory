from django.urls import path
from . import views

urlpatterns = [
    
    path('dashboard/', views.account_dashboard, name='account_dashboard'),
    path('transaction/new/', views.create_transaction, name='create_transaction'),

    path('credits/', views.credit_list, name='credit_list'),
    path('debits/', views.debit_list, name='debit_list'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('finance-summary/', views.finance_summary, name='summary'),
    
    path('add-credit/', views.add_credit, name='add_credit'),
    path('add-debit/', views.add_debit, name='add_debit'),
    path('add-transaction-history/', views.add_transaction_history, name='add_transaction_history'),
    path('add-finance-summary/', views.add_finance_summary, name='add_finance_summary'),
    
    
]



