
from django.core.exceptions import ValidationError
from django.test import TestCase,tag
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import NO, YES, OTHER
from .models import ListModel
from ..form_validators import Covid19SymptomaticInfectionsFormValidator


@tag('symp') 
class TestCovid19SymptomaticInfections(TestCase):
    
    
    def setUp(self):
        
        
        self.options = {
            'symptomatic_experiences': NO,
        }

    def test_symptomatic_infections_specify_required(self):
        """ Assert that the Symptomatic Infections other specify raises an error if 
        Symptomatic Infections
        includes other but symptomatic_infections_other not specified.
        """
        ListModel.objects.create(name=OTHER)
        self.options.update(
            symptomatic_experiences=YES,
            symptomatic_infections=ListModel.objects.all(),
            date_of_infection=(get_utcnow() - relativedelta(days=10)).date(),
            symptomatic_infections_other=None)
        form_validator = Covid19SymptomaticInfectionsFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('symptomatic_infections_other', form_validator._errors)

    def test_symptomatic_infections_specify_valid(self):
        """ Tests if Symptomatic Infections other includes other symptomatic_infections_other
            tests if the Validation Error is raised unexpectedly.
        """
        ListModel.objects.create(name=OTHER)
        self.options.update(
            symptomatic_experiences=YES,
            symptomatic_infections=ListModel.objects.all(),
            date_of_infection=(get_utcnow() - relativedelta(days=10)).date(),
            symptomatic_infections_other='blah')
        form_validator = Covid19SymptomaticInfectionsFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
     
      
    def test_symptomatic_infections_required(self):
        """ Assert that the Symptomatic Infections are required when symptoms are experienced.
        """
        self.options.update(
            symptomatic_experiences = YES)

        form_validator = Covid19SymptomaticInfectionsFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('symptomatic_infections', form_validator._errors)
    
    
    def test_symptomatic_infections_valid(self):
        """ Catch unexpected errors when the symptomatic_experiences is yes and symptoms given.
        """
        ListModel.objects.create(name='test')
        self.options.update(
            symptomatic_experiences=YES,
            symptomatic_infections=ListModel.objects.all(),
            date_of_infection=(get_utcnow() - relativedelta(days=10)).date(),
        )

        form_validator = Covid19SymptomaticInfectionsFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
            
        
    def test_hospitalization_date_invalid(self):
        """ Assert that the Hospitalization date is required when hospitald visit is specified.
        """
        self.options.update(
            hospitalisation_visit = YES)

        form_validator = Covid19SymptomaticInfectionsFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hospitalisation_date', form_validator._errors)
        
    
    def test_symptomatic_infections_valid(self):
        """ Assert that when Hospitalization date is specified no unexpected error is raise.
        """
        self.options.update(
            hospitalisation_visit=YES,
            hospitalisation_date=(get_utcnow() - relativedelta(days=10)).date(),
        )

        form_validator = Covid19SymptomaticInfectionsFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')   

