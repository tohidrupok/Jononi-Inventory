from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator 
from django.utils.timezone import now 


class PositiveDecimalField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('validators', []).append(MinValueValidator(0))
        super().__init__(*args, **kwargs)  
        

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = PositiveDecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_type = models.CharField(
        max_length=50,
        choices=[('SR', 'SR'), ('Dealer', 'Dealer'), ('Admin', 'Admin'), ('HOS', 'HOS'), ('ROS', 'ROS'), ('Accounts', 'Accounts')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_type} - Balance: {self.balance}"

    def update_balance(self, amount):
        """Updates the account balance based on transaction amount."""
        self.balance += amount
        self.save()

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=50,
        choices=[('Credit', 'Credit'), ('Debit', 'Debit')]
    )
    amount = PositiveDecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.transaction_date}"

    def save(self, *args, **kwargs):
        """Override save to update account balance when a transaction is made."""
        if self.transaction_type == 'Debit':
            self.account.update_balance(-self.amount)
        elif self.transaction_type == 'Credit':
            self.account.update_balance(self.amount)
        super().save(*args, **kwargs)


class Source(models.Model): 
    name = models.CharField(max_length=255)  
    date = models.DateField(default=now) 
    note = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name
 
        
class Credit(models.Model):  
       
    CREDIT_TYPE_CHOICES = [
        ('loan_bank', 'Loan from Bank'),
        ('own_investment', 'Own Investment'),
        ('order_price', 'Demand item Price'),
    ]

    type = models.CharField(max_length=20, choices=CREDIT_TYPE_CHOICES)
    amount = PositiveDecimalField(max_digits=12, decimal_places=2) 
    persantage = PositiveDecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    returned_amount = PositiveDecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now)
    source = models.ForeignKey( 
        Source, 
        on_delete=models.CASCADE,  
        related_name='credits'  , blank=True, null=True
    )

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount}" 

class Debit(models.Model):
    DEBIT_TYPE_CHOICES = [
        ('cashout', 'Cashout'),
        ('office_cost', 'Office Management Cost'),
        ('factory_demand', 'Factory Demand Cash'),
    ]

    type = models.CharField(max_length=20, choices=DEBIT_TYPE_CHOICES)
    amount = PositiveDecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now)

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount}"

class TransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    details = models.CharField(max_length=10, null=True, blank= True)
    amount = PositiveDecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now, blank=True, null=True )

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount}"

class FinanceSummary(models.Model):
    month = models.DateField()
    total_credit = PositiveDecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_debit = PositiveDecimalField(max_digits=12, decimal_places=2, default=0.00)
    monthly_profit = PositiveDecimalField(max_digits=12, decimal_places=2, default=0.00)

    def calculate_profit(self):
        self.monthly_profit = self.total_credit - self.total_debit
        self.save()

    def __str__(self):
        return f"Summary for {self.month.strftime('%B %Y')} - Profit: {self.monthly_profit}"



