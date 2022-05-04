from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from esr21_subject_validation.form_validators.outcome_inline_form_validator import \
    OutcomeInlineFormValidator


@tag('preg_outcome')
class TestOutcomeInlineFormValidator(TestCase):

    def test_method_specify(self):
        clean_data = {
            'method': 'full_term',
            'specify_outcome': 'full_term'
        }

        form_validator = OutcomeInlineFormValidator(
            cleaned_data=clean_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
