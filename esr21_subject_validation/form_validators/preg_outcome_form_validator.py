from edc_form_validators import FormValidator

from esr21_subject_validation.form_validators.crf_form_validator import CRFFormValidator


class OutcomeInlineFormValidator(CRFFormValidator, FormValidator):
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