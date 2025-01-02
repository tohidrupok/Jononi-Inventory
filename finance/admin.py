from django.contrib import admin

from .models import Account, Transaction, Credit, Debit, TransactionHistory, FinanceSummary, Source

# Register your models here.
admin.site.register(Account)
admin.site.register(Transaction)

admin.site.register(Source)
admin.site.register(Credit)
admin.site.register(Debit)
admin.site.register(TransactionHistory)
admin.site.register(FinanceSummary)
