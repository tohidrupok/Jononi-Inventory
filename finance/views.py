from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction
from .forms import TransactionForm
from dashboard.decorators import allowed_users 
from .models import Credit, Debit, TransactionHistory, FinanceSummary
from .forms import CreditForm, DebitForm, TransactionHistoryForm, FinanceSummaryForm
from django.core.paginator import Paginator

#user bank management
@login_required
def account_dashboard(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-transaction_date')
    return render(request, 'account_dashboard.html', {'account': account, 'transactions': transactions})

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = Account.objects.get(user=request.user)
            transaction.save()
            return redirect('account_dashboard')
    else:
        form = TransactionForm()

    return render(request, 'create_transaction.html', {'form': form})


#System bank management

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def credit_list(request):
    credits = Credit.objects.all().order_by('-id') 
    paginator = Paginator(credits, 30)  
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    is_finance = request.user.groups.filter(name='Finance').exists()
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    context = {
        'page_obj': page_obj,
        'is_finance': is_finance,
        'is_admin': is_admin,
    }
    return render(request, 'finance/credit_list.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def debit_list(request):
    debits = Debit.objects.all().order_by('-id') 
    paginator = Paginator(debits, 30) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_finance = request.user.groups.filter(name='Finance').exists()
    is_admin = request.user.groups.filter(name='Admin').exists() 
    
    context = {
        'page_obj': page_obj,
        'is_finance': is_finance,
        'is_admin': is_admin,
    }
    return render(request, 'finance/debit_list.html', context)



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def transaction_history(request):
    transactions = TransactionHistory.objects.all().order_by('-id')
    
    # Pagination logic
    paginator = Paginator(transactions, 60)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    is_finance = request.user.groups.filter(name='Finance').exists()
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    context = {
        'page_obj': page_obj, 
        'is_finance': is_finance,
        'is_admin': is_admin,
    }
    
    return render(request, 'finance/transaction_history.html', context)

from django.db.models import Sum
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def finance_summary(request):
    # Aggregating total amounts for each credit type
    credit_totals = (
        Credit.objects.values('type')
        .annotate(total_amount=Sum('amount'))
        .order_by('type')
    )

    # Aggregating total amounts for each debit type
    debit_totals = (
        Debit.objects.values('type')
        .annotate(total_amount=Sum('amount'))
        .order_by('type')
    )
    
    # Preparing a dictionary for easy template rendering
    credit_summary = {item['type']: item['total_amount'] for item in credit_totals}
    debit_summary = {item['type']: item['total_amount'] for item in debit_totals}

    # Default values for missing types
    loan_bank = credit_summary.get('loan_bank', 0)
    own_investment = credit_summary.get('own_investment', 0)
    order_price = credit_summary.get('order_price', 0)

    cashout = debit_summary.get('cashout', 0)
    office_cost = debit_summary.get('office_cost', 0)
    factory_demand = debit_summary.get('factory_demand', 0)

    # Checking if the user belongs to the Finance group
    is_finance = request.user.groups.filter(name='Finance').exists()
    is_admin = request.user.groups.filter(name='Admin').exists()

    context = {
        'loan_bank': loan_bank,
        'own_investment': own_investment,
        'order_price': order_price,
        'cashout': cashout,
        'office_cost': office_cost,
        'factory_demand': factory_demand,
        'is_finance': is_finance,
        'is_admin': is_admin,
    }
    return render(request, 'finance/finance_summary.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def add_credit(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            credit = form.save()

            if credit.source:
                description = f"I have secured a loan to meet my financial requirements from {credit.source.name}"
            else:
                description = "I have secured a loan to meet my financial requirements from an unknown source"

            # Create the transaction history
            TransactionHistory.objects.create(
                transaction_type='credit',
                details = credit.get_type_display(),
                amount=credit.amount,
                description=description, 
                date=credit.date
            )

            return redirect('credit_list')
    else:
        form = CreditForm()
    is_finance = request.user.groups.filter(name='Finance').exists()
    is_admin = request.user.groups.filter(name='Admin').exists()
    return render(request, 'finance/add_credit.html', {'form': form,'is_finance':is_finance,'is_admin':is_admin})

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def add_debit(request):
    if request.method == 'POST':
        form = DebitForm(request.POST)
        if form.is_valid():
            debit = form.save()

            # Create the transaction history
            TransactionHistory.objects.create(
                transaction_type='Debit',
                details = debit.get_type_display(),
                amount=debit.amount,
                description=debit.description, 
            )

            return redirect('debit_list')
    else:
        form = DebitForm()
    is_finance = request.user.groups.filter(name='Finance').exists()
    is_admin = request.user.groups.filter(name='Admin').exists() 
    
    return render(request, 'finance/add_debit.html', {'form': form,'is_finance':is_finance,'is_admin':is_admin})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def add_transaction_history(request):
    if request.method == 'POST':
        form = TransactionHistoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_history')
    else:
        form = TransactionHistoryForm()
    return render(request, 'finance/add_transaction_history.html', {'form': form})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance','Admin'])
def add_finance_summary(request):
    if request.method == 'POST':
        form = FinanceSummaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance_summary')
    else:
        form = FinanceSummaryForm()
    return render(request, 'finance/add_finance_summary.html', {'form': form})

