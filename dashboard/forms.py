from django import forms
from .models import Product, Order, Shop, DealerProductNeed, FinalOrder, DealerOrder


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['shop_name', 'shop_owner', 'shop_phone', 'zone']


class OrderForm(forms.ModelForm):
    product_tp = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label='পণ্যের মূল্য (KG)' ,
        widget=forms.NumberInput(attrs={'readonly': 'readonly'}),
    )

    class Meta:
        model = Order
        fields = ['name', 'product_tp', 'order_quantity']
        labels = {
            'name': 'পণ্য নির্বাচন করুন (অত্যাবশ্যক)', 
            'product_tp': 'পণ্যের TP',
            'order_quantity': 'পণ্যের পরিমাণ(KG) নির্ধারণ করুন (অত্যাবশ্যক)', 
            
        }

        
class ExpenceOrderForm(forms.ModelForm):

    class Meta:
        model = FinalOrder
        fields = ['expense_Amount', 'expense_type']
        labels = {
            'expense_Amount': ' টাকার পরিমাণ নির্ধারণ করুন (অত্যাবশ্যক)' ,
            'expense_type': ' খরচের ধরণ নির্বাচন করুন (অত্যাবশ্যক)', 
            
        }
        
        

class editOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['name', 'order_quantity','product_tp'] 
        
class noteOrderForm(forms.ModelForm):

    class Meta:
        model = FinalOrder
        fields = ['note_amount','note_write']  


class DateSelectForm(forms.Form):
    date = forms.DateField(
        widget=forms.SelectDateWidget(),
        label="Select Date",
    )


class DealerProductNeedForm(forms.ModelForm):
    class Meta:
        model = DealerProductNeed
        fields = ['product', 'demand_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class editdemandForm(forms.ModelForm):

    class Meta:
        model = DealerProductNeed
        fields = ['product', 'demand_quantity']



class PaidDemandForm(forms.ModelForm):

    class Meta:
        model = DealerOrder
        fields = ['note_amount','note_write']  
        
        
class ExpenceDemandForm(forms.ModelForm):

    class Meta:
        model = DealerOrder
        fields = ['expense_Amount', 'expense_type']
        labels = {
            'expense_Amount': ' টাকার পরিমাণ নির্ধারণ করুন (অত্যাবশ্যক)' ,
            'expense_type': ' খরচের ধরণ নির্বাচন করুন (অত্যাবশ্যক)', 
            
        }