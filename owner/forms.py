# forms.py
from django import forms
from dashboard.models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['product', 'discount_percentage', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['discount_percentage'].widget.attrs.update({'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control datetimepicker'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control datetimepicker'})
