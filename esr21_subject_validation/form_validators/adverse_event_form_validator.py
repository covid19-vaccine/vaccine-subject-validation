from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES
from edc_form_validators import FormValidator


class AdverseEventFormValidator(FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
        self.validate_ae_end_date(cleaned_data=cleaned_data)
        self.validate_outcome(cleaned_data=cleaned_data)
        self.validate_maae()

    def validate_ae_end_date(self, cleaned_data=None):
        self.required_if(
            'resolved',
            field='status',
            field_required='resolution_date',
            required_msg='AE is resolved, please provide the AE end date')

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('resolution_date', None)

        if end_date and end_date < start_date:
            message = {'resolution_date':
                       'AE end date can not be before AE start date'}
            self._errors.update(message)
            raise ValidationError(message)

    def validate_outcome(self, cleaned_data=None):
        status = cleaned_data.get('status')
        outcome = cleaned_data.get('outcome')
        if status == 'resolved':
            if outcome not in ['resolved', 'resolved_with_sequelae']:
                message = {'outcome':
                           f'Status of the AE is {status}, please revise the outcome'}
                self._errors.update(message)
                raise ValidationError(message)
        else:
            if outcome in ['resolved', 'resolved_with_sequelae']:
                message = {'outcome':
                           f'Status of the AE is {status}, please revise the outcome'}
                self._errors.update(message)
                raise ValidationError(message)

        self.required_if(
            'resolved_with_sequelae',
            field='outcome',
            field_required='sequelae_specify')

    def validate_maae(self):
        self.required_if(
            YES,
            field='medically_attended_ae',
            field_required='maae_specify')
