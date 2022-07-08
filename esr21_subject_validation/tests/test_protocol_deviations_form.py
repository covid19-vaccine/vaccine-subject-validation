from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from ..form_validators import ProtocolDeviationFormValidator

@tag('pdev')
class TestProtocolDeviationsForm(TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(ProtocolDeviationFormValidator, *args, **kwargs)

    def setUp(self):
        self.options = {
            'deviation_name': None,
        }
    
    def test_covid_symptoms_invalid(self):
        """ Assert that if the participant has had prior covid infection then symptoms
         are required.
        """
        self.options['deviation_name'] = 'test'

        form_validator = ProtocolDeviationFormValidator(
            cleaned_data=self.medical_history_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('subject_identifiers', form_validator._errors)