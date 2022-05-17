from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import NO, YES

from ..form_validators import AdverseEventRecordFormValidator
from .models import Appointment, SubjectVisit
from django.test.utils import tag


@tag('ae')
class TestAdverseEventRecordFormValidator(TestCase):

    def setUp(self):
        subject_identifier = '1234567'
        appointment = Appointment.objects.create(
            subject_identifier=subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1001')
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment)
        self.ae_options = {
            'subject_visit': subject_visit,
            'start_date': get_utcnow().date(),
            'ae_grade': 'mild',
            'study_treatmnt_rel': 'not_related',
            'nonstudy_treatmnt_rel': 'related',
            'studyproc_treatmnt_rel': 'not_related',
            'action_taken': 'drug_withdrawal',
            'outcome': 'unknown',
            'serious_event': NO,
            'special_interest_ae': NO,
            'medically_attended_ae': NO,
            'treatment_given': NO,
            'ae_study_discontinued': NO,
            'covid_related_ae': YES}

    def test_ae_status_resolved_end_date_valid(self):
        """ Tests if the AE status is `resolved` and end date is given, cleaned
            data validates or fails the tests if the Validation Error is raised
            unexpectedly.
            TO DO: Refactor!!
        """
        self.ae_options.update(stop_date=get_utcnow().date(),
                               outcome='resolved')
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_ae_end_dt_before_start_dt_invalid(self):
        """ Assert that the AE end date raises an error if end date is before
            the start date of the AE.
        """
        self.ae_options.update(stop_date=get_utcnow().date() - relativedelta(days=2),
                               outcome='resolved')
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('stop_date', form_validator._errors)

    def test_ae_end_dt_after_start_dt_valid(self):
        """ Tests if the AE end date is after the start date, cleaned data
            validates or fails the tests if the Validation Error is raised
            unexpectedly.
        """
        self.ae_options.update(start_date=get_utcnow().date() - relativedelta(months=2),
                               stop_date=get_utcnow().date() - relativedelta(days=23),
                               outcome='resolved')
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_ae_outcome_resolved_w_sequelae_specify(self):
        """ Assert that the AE sequelae specify raises an error if outcome is
            is resolved with sequelae, but not specified.
        """
        self.ae_options.update(stop_date=get_utcnow().date(),
                               outcome='resolved_with_sequelae')
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('sequelae_specify', form_validator._errors)

    def test_ae_outcome_resolved_w_sequelae_stated(self):
        """ Tests if AE outcome is `resolved with sequelae` and specified,
            cleaned data validates or fails the tests if the Validation Error
            is raised unexpectedly.
        """
        self.ae_options.update(stop_date=get_utcnow().date(),
                               outcome='resolved_with_sequelae',
                               sequelae_specify='blah')
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_maae_yes_specify_required(self):
        """ Assert that if MAAE is `yes`, error is raised if MAAE is not specified.
        """
        self.ae_options.update(medically_attended_ae=YES)
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('maae_specify', form_validator._errors)

    def test_maae_yes_specify_valid(self):
        """ Tests if MAAE is `yes` and specified, cleaned data validates or
            fails the tests if the Validation Error is raised unexpectedly.
        """
        self.ae_options.update(medically_attended_ae=YES,
                               maae_specify='blah')
        form_validator = AdverseEventRecordFormValidator(
            cleaned_data=self.ae_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
