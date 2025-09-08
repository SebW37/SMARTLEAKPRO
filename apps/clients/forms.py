"""
Django forms for client management.
"""
from django import forms
from .models import Client, ClientContact, ClientContract, ClientSite


class ClientForm(forms.ModelForm):
    """Form for creating and editing clients."""
    
    class Meta:
        model = Client
        fields = [
            'name', 'client_type', 'status', 'email', 'phone', 'secondary_email', 
            'secondary_phone', 'address', 'city', 'postal_code', 'country',
            'contract_type', 'contract_start_date', 'contract_end_date',
            'billing_address', 'billing_city', 'billing_postal_code',
            'siret', 'siren', 'vat_number', 'preferred_payment_method',
            'bank_details', 'visit_preferences', 'access_constraints',
            'preferred_visit_days', 'preferred_visit_hours', 'notes',
            'gdpr_consent', 'data_retention_until'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'client_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'secondary_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'secondary_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'contract_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'billing_city': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'siret': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 14}),
            'siren': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 9}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_payment_method': forms.Select(attrs={'class': 'form-select'}),
            'bank_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'visit_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'access_constraints': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preferred_visit_days': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_visit_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'gdpr_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_retention_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make required fields more obvious
        self.fields['name'].required = True
        self.fields['city'].required = True
        self.fields['postal_code'].required = True


class ClientContactForm(forms.ModelForm):
    """Form for creating and editing client contacts."""
    
    class Meta:
        model = ClientContact
        fields = [
            'first_name', 'last_name', 'role', 'position', 'email', 
            'phone', 'mobile', 'notes', 'is_primary'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class ClientContractForm(forms.ModelForm):
    """Form for creating and editing client contracts."""
    
    class Meta:
        model = ClientContract
        fields = [
            'contract_number', 'contract_type', 'status', 'start_date', 
            'end_date', 'renewal_date', 'monthly_amount', 'annual_amount',
            'currency', 'description', 'terms_conditions', 'special_conditions'
        ]
        widgets = {
            'contract_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'renewal_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'annual_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'special_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract_number'].required = True
        self.fields['start_date'].required = True


class ClientSiteForm(forms.ModelForm):
    """Form for creating and editing client sites."""
    
    class Meta:
        model = ClientSite
        fields = [
            'name', 'description', 'address', 'city', 'postal_code', 'country',
            'contact_name', 'contact_phone', 'contact_email', 'access_instructions', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'access_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['postal_code'].required = True


class ClientSearchForm(forms.Form):
    """Form for client search and filtering."""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, numéro, email, téléphone, ville...'
        })
    )
    client_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Client.CLIENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Client.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('name', 'Nom'),
            ('created', 'Date de création'),
            ('type', 'Type'),
            ('status', 'Statut'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
