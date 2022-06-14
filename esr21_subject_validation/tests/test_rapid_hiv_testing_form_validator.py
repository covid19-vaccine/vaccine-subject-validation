from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import POS, YES, NO, NOT_APPLICABLE

from ..form_validators import RapidHivTestingFormValidator

@tag('hivt')
class TestRapidHivTestingForm(TestCase):

    def setUp(self):

        # self.rapid_hiv_testing_options = {
        #     'rapid_test_done': YES,
        #     'result_date': get_utcnow(),
        #     'result': POS, }
        
        self.options = {
            'rapid_test_done': YES,
            'result_date': get_utcnow(),
            'result': POS, 
            'hiv_testing_consent': NO,
            'prev_hiv_test': YES,
            'hiv_test_date': get_utcnow(),}

    def test_rapid_hiv_testing(self):
        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.rapid_hiv_testing_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_result_invalid(self):
        self.rapid_hiv_testing_options['result'] = None

        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.rapid_hiv_testing_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('result', form_validator._errors)
    
    @tag('ptdi')
    def test_prev_test_date_invalid(self):
        self.options.update({'hiv_test_date': None })

        form_validator = RapidHivTestingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hiv_test_date', form_validator._errors) 
    
    @tag('ptdv')
    def test_prev_test_date_valid(self):
        self.options.update({
            'hiv_test_date':(get_utcnow() - relativedelta(months=1)).date()
            })
        
        form_validator = RapidHivTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
        
