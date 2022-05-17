from django.core.exceptions import ValidationError
from edc_constants.choices import NO
from edc_form_validators import FormValidator
from django import forms


class DemographicsDataFormValidator(FormValidator):

    def clean(self):
        """
        All validations defined in directly on the forms will be called by the super
        """
        super().clean()

        """
        Will make the {varable}_other required
        """
        self.validate_other_specify(field='ethnicity')
        self.validate_other_specify(field='employment_status')
        self.validate_other_specify(field='marital_status')

        """
        Number of people in a household cannot be negative
        """
        household_members = self.cleaned_data.get('household_members')

        if household_members and int(household_members) < 0:
            raise ValidationError({'household_members': 'Number cannot be negative'})
