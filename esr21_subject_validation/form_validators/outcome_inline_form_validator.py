from edc_form_validators import FormValidator


class OutcomeInlineFormValidator(FormValidator):
    def clean(self):
        self.required_if(
            'full_term',
            field_required='method',
            field='specify_outcome',
            inverse=False
        )
        self.required_if(
            'premature',
            field_required='method',
            field='specify_outcome',
            inverse=False
        )
