from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.RadioSelect(),
    )

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0')
        return amount

    class Meta:
        model = Transaction
        fields = (
            'type',
            'amount',
            'date',
            'category',
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'min': 0.10, 'placeholder': '0.00', 'step': 0.1}),
        }
