import requests
from django import forms
from django.conf import settings  
BASE_URL = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000/')



class MemberForm(forms.Form):
    member_id = forms.CharField(max_length=20, label="Member ID", required=False)
    full_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, is_update=False, **kwargs):
        super().__init__(*args, **kwargs)

        
        if not is_update:
            try:
                response = requests.get(f"{BASE_URL}/api/members/")
                if response.status_code == 200:
                    members = response.json()
                    if members:
                        last_member_id = members[-1].get('member_id', 'M0000')
                        last_number = int(last_member_id.replace("M", ""))
                        new_number = last_number + 1
                    else:
                        new_number = 1
                else:
                    new_number = 1
            except Exception:
                new_number = 1

            self.fields['member_id'].initial = f"M{new_number:04d}"

        
        self.fields['member_id'].widget.attrs['readonly'] = True

    def clean_member_id(self):
        
        member_id = self.cleaned_data.get('member_id')
        if not member_id:
            member_id = self.fields['member_id'].initial
        return member_id



class WalletForm(forms.Form):
    member_id = forms.CharField(max_length=20)
    balance = forms.DecimalField(max_digits=12, decimal_places=2, initial=0)



class TransactionForm(forms.Form):
    TRANSACTION_CHOICES = (
        ('TRANSFER', 'transfer'),
        ('WITHDRAW', 'Withdraw'),
    )

    member_one = forms.CharField(label="Sender (Member One)", max_length=20)
    member_two = forms.CharField(label="Receiver (Member Two)", max_length=20, required=False)
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES)
    description = forms.CharField(widget=forms.Textarea, required=False)