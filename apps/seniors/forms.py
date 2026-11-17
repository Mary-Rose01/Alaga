from datetime import date

from django import forms

from .models import SeniorCitizen


def _age(birth_date):
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


class SeniorRegistrationForm(forms.ModelForm):
    """Registration of a senior citizen record (NOT a user/worker account)."""

    # Emergency contact
    contact_person = forms.CharField(max_length=200, required=False)
    contact_relationship = forms.CharField(max_length=100, required=False)
    contact_phone = forms.CharField(max_length=100, required=False)

    # Health background (comma separated free text)
    chronic_conditions = forms.CharField(required=False)
    allergies = forms.CharField(required=False)

    consent = forms.BooleanField(
        required=True,
        error_messages={'required': 'Consent must be confirmed before submitting.'},
    )

    class Meta:
        model = SeniorCitizen
        fields = [
            'first_name', 'middle_name', 'last_name', 'suffix', 'birth_date', 'sex',
            'civil_status', 'blood_type', 'living_arrangement', 'contact_number',
            'osca_id', 'philhealth_number', 'street_address', 'barangay',
            'city_municipality', 'province',
        ]
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barangay'].required = True
        self.fields['sex'].required = True

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date > date.today() or _age(birth_date) < 60:
            raise forms.ValidationError('Senior citizens must be at least 60 years old.')
        return birth_date

    def clean_osca_id(self):
        return (self.cleaned_data.get('osca_id') or '').strip() or None

    def clean_philhealth_number(self):
        return (self.cleaned_data.get('philhealth_number') or '').strip() or None
