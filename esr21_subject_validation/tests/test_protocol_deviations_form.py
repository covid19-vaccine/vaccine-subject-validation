from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from django.core.exceptions import ValidationError
from ..form_validators import ProtocolDeviationFormValidator

@tag('pdev')
class TestProtocolDeviationsForm(TestCase):
    
    def setUp(self):
        self.options = {
            'report_datetime':  get_utcnow().date(),
            'deviation_name': 'test',
            'subject_identifiers': 'test',
            'deviation_description':'test',
            'deviation_form_name': 'test',
            'comment':'test'
        }
        
        
    def test_deviations_valid(self):
        """ Test to check if the form is valid .
        """
        form_validator = ProtocolDeviationFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')   
            
            
    def test_deviation_name_invalid(self):
        
        cleaned_data = {
            'report_datetime':  get_utcnow().date(),
            'deviation_name': None,
            'subject_identifiers': None,
            'deviation_description': None,
            'deviation_form_name': None,
            'comment':'test'
        }
        form_validator = ProtocolDeviationFormValidator(cleaned_data=cleaned_data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('deviation_name', form_validator._errors)
        
    def test_subject_idxs_required(self):
        self.options.update({'subject_identifiers': None})
        form_validator = ProtocolDeviationFormValidator(cleaned_data=self.options)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('subject_identifiers', form_validator._errors)
        
    def test_deviation_form_name_required(self):
        self.options.update({'deviation_form_name': None})
        form_validator = ProtocolDeviationFormValidator(cleaned_data=self.options)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('deviation_form_name', form_validator._errors)
        
    def test_deviation_desc_required(self):
        self.options.update({'deviation_description': None})
        form_validator = ProtocolDeviationFormValidator(cleaned_data=self.options)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('deviation_description', form_validator._errors)
            
                 
