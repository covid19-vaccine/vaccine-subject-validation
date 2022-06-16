from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import POS, YES, NEG, NO, NOT_APPLICABLE

from ..form_validators import RapidHivTestingFormValidator

@tag('hivt')
class TestRapidHivTestingForm(TestCase):

    def setUp(self):

        self.options = {
            'rapid_test_done': YES,
            'result_date': get_utcnow(),
            'rapid_test_result': POS, 
            'hiv_testing_consent': NO,
            'prev_hiv_test': YES,
            'hiv_test_date': get_utcnow(),}

    def test_rapid_hiv_testing(self):
        
        self.options.update({'hiv_testing_consent': YES})
        self.options.update({'prev_hiv_test': NO})
        self.options.update({'hiv_test_date': None})
        self.options.update({'rapid_test_result': NEG})
        self.options.update({'rapid_test_date': get_utcnow() })
        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_result_invalid(self):
        self.options.update({'rapid_test_result': None})
        self.options.update({'hiv_testing_consent': YES})
        self.options.update({'prev_hiv_test': NO})
        self.options.update({'rapid_test_date': get_utcnow() })
        self.options.update({'evidence_hiv_status': NO })

        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('rapid_test_result', form_validator._errors)
    

    def test_prev_test_date_invalid(self):
        self.options.update({'hiv_test_date': None })

        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hiv_test_date', form_validator._errors) 
    

    def test_prev_test_date_valid(self):
        self.options.update({
            'hiv_test_date':(get_utcnow() - relativedelta(months=4)).date()
            })
        self.options.update({'hiv_testing_consent':NO})
        self.options.update({'prev_hiv_test':YES})
        self.options.update({'hiv_result':POS})
        self.options.update({'evidence_hiv_status': YES })
        self.options.update({'rapid_test_date': get_utcnow() })
        
        form_validator = RapidHivTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
            

    def test_prev_test_evidence_valid(self):
        self.options.update({'evidence_hiv_status': NO })

        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('prev_hiv_test', form_validator._errors)         
        
