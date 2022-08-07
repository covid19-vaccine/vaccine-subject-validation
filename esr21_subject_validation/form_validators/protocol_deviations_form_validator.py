from edc_form_validators import FormValidator
from django.core.exceptions import ValidationError

class ProtocolDeviationFormValidator(FormValidator):
    
    def clean(self):
        super().clean()
    
        required_fields = ['deviation_form_name','deviation_name',
                           'subject_identifiers','deviation_description']
        
        for r_field in required_fields:
            self.required_if_not_none(
                field='deviation_name',
                field_required=r_field)
            
        deviation_name = self.cleaned_data.get('deviation_name')
        if deviation_name is None:
            message = {'deviation_name':
                           ('A protocol deviation name has to be provided')}
            raise ValidationError(message)
            
                 
            