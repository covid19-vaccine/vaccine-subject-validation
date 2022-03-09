from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, OTHER, YES

from ..form_validators import HospitalisationFormValidator
from .models import ListModel

from .models import Appointment, SubjectVisit


class TestHospitalizationForm(TestCase):

    def setUp(self):
        subject_identifier = '1234567'
        appointment = Appointment.objects.create(
            subject_identifier=subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1001')
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment)
        HospitalisationFormValidator.demographics_data_model = \
            'esr21_subject_validation.hospitalization'

        ListModel.objects.create(name='symptoms')
        self.hospitalization_options = {
            'status': 'er',
            'start_date': get_utcnow().date(),
            'stop_date': None,
            'ongoing': YES,
            'reason': 'covid19_related_symptoms',
            'reason_other': None,
            'covid_symptoms': ListModel.objects.all()}

    def test_hospitialization_data(self):

        form_validator = HospitalisationFormValidator(
            cleaned_data=self.hospitalization_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_stop_date_invalid(self):
        """ Assert that stop date raises an error if ongoing is NO
        """
        self.hospitalization_options['ongoing'] = NO

        form_validator = HospitalisationFormValidator(
            cleaned_data=self.hospitalization_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('stop_date', form_validator._errors)

    def test_reason_other_invalid(self):
        """ Assert that reason_other raises an error if reason is not other
        """
        self.hospitalization_options['reason'] = OTHER

        form_validator = HospitalisationFormValidator(
            cleaned_data=self.hospitalization_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_other', form_validator._errors)

    def test_medical_event_specify_invalid(self):

        ListModel.objects.create(name=OTHER)
        self.hospitalization_options.update(
            covid_symptoms=None,
            reason='covid')
        form_validator = HospitalisationFormValidator(
            cleaned_data=self.hospitalization_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
