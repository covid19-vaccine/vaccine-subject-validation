from edc_constants.constants import NOT_APPLICABLE
from edc_form_validators import FormValidator
from .crf_form_validator import CRFFormValidator


class SubjectRequisitionFormValidator(CRFFormValidator, FormValidator):

    def clean(self):
        super().clean()

        self.validate_other_specify(field='reason_not_drawn')
        self.validate_other_specify(field='item_type')
        self.not_required_if(NOT_APPLICABLE, field='item_type', field_required='item_count')
        self.required_if('urgent', field='priority', field_required='urgent_specify')
