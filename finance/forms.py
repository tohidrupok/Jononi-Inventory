from django import forms
from .models import Transaction
from .models import Credit, Debit, TransactionHistory, FinanceSummary

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


# System Finance/Banking
class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['type','source','amount', 'persantage','returned_amount' ,'description'] 

class DebitForm(forms.ModelForm):
    class Meta:
        model = Debit
        fields = ['type', 'amount', 'description' ]

class TransactionHistoryForm(forms.ModelForm):
    class Meta:
        model = TransactionHistory
        fields = ['transaction_type', 'amount', 'description', 'date']

class FinanceSummaryForm(forms.ModelForm):
    class Meta:
        model = FinanceSummary
        fields = ['month', 'total_credit', 'total_debit', 'monthly_profit']


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
