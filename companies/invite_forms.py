from django import forms
from .models import CompanyInvite, CompanyRole

class InviteForm(forms.ModelForm):
    class Meta:
        model = CompanyInvite
        fields = ("email", "role")
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "admin@entreprise.com"}),
            "role": forms.Select()
        }
