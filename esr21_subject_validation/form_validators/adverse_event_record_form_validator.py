from django.core.exceptions import ValidationError
from edc_constants.constants import YES
from edc_form_validators import FormValidator


class AdverseEventRecordFormValidator(FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
        self.validate_ae_end_date(cleaned_data=cleaned_data)
        self.validate_outcome()
        self.validate_maae()
        self.validate_treatment_given()
        self.validate_discontinuation()

    def validate_ae_end_date(self, cleaned_data=None):
        self.required_if(
            'resolved',
            field='status',
            field_required='stop_date',
            required_msg='AE is resolved, please provide the AE end date')

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('stop_date', None)

        if end_date and end_date < start_date:
            message = {'stop_date':
                       'AE end date can not be before AE start date'}
            self._errors.update(message)
            raise ValidationError(message)

    def validate_outcome(self):
        self.required_if(
            'resolved_with_sequelae',
            field='outcome',
            field_required='sequelae_specify')

    def validate_maae(self):
        self.required_if(
            YES,
            field='medically_attended_ae',
            field_required='maae_specify')

    def validate_treatment_given(self):
        self.required_if(
            YES,
            field='treatment_given',
            field_required='treatmnt_given_specify')

    def validate_discontinuation(self):
        self.required_if(
            YES,
            field='ae_study_discontinued',
            field_required='discontn_dt')
