from edc_form_validators import FormValidator


class ProtocolDeviationFormValidator(FormValidator):
    
    
    def clean(self):
        super().clean()

    # subject identifier required when deviation name is given
        self.required_if_not_none(
            field='deviation_name',
            field_required='subject_identifiers',
            required_msg='Please select an identifier')