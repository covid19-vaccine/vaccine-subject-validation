from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base import get_utcnow

from .models import Appointment, SubjectVisit, VaccinationDetails
from ..constants import FIRST_DOSE, SECOND_DOSE
from ..form_validators import VaccinationHistoryFormValidator


@tag('history')
class TestVaccinationHistoryFormValidator(TestCase):

    def setUp(self):
        vaccination_details_cls = 'esr21_subject_validation.vaccinationdetails'
        VaccinationHistoryFormValidator.vaccination_details_cls = vaccination_details_cls

        self.subject_identifier = '111111'

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000',
            schedule_name='esr21_enrol_schedule')

        self.visit_1000 = SubjectVisit.objects.create(
            appointment=appointment,
            schedule_name='esr21_enrol_schedule')

        self.appt_1070 = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1070',
            schedule_name='esr21_fu_schedule',
            appt_datetime=get_utcnow())

        self.visit_1070 = SubjectVisit.objects.create(
            appointment=self.appt_1070,
            schedule_name='esr21_fu_schedule')

    # matching vac details and dose quantity with no product
    # matching vac details and dose quantity with a product

    @tag('doses')
    def test_number_of_doses(self):
        """
        catch a validation error if product names is not azd_1222
        """

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '2',
            'dose1_product_name': 'azd_1',
            'dose1_date': get_utcnow().date(),
            'dose2_product_name': 'azd_12',
            'dose2_date': get_utcnow().date(),
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        try:
            form_validator.validate()
        except Exception as e:
            self.fail(f'failed to validate with error:{e}')

    @tag('doses_1')
    def test_number_of_doses_matching_vac_details_and_dose_quantity_with_no_product(self):
        """
        raise an error if matching vac details and dose quantity with no product
        """
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '1',
            'dose1_product_name': 'azd_1',
            'dose2_product_name': None,
            'dose1_date': get_utcnow().date(),
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose_quantity', form_validator._errors)

    def test_first_dose(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '1',
            'dose2_product_name': None,
            'dose1_product_name': 'vin'
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose_quantity', form_validator._errors)

    def test_first_dose_date(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        VaccinationDetails.objects.create(
            subject_visit=self.visit_1070,
            report_datetime=(get_utcnow() + relativedelta(days=56)).date(),
            received_dose_before=SECOND_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '2',
            'dose1_product_name': 'azd_12',
            'dose1_date': get_utcnow().date(),
            'dose2_product_name': 'azd_12',
            'dose2_date': (get_utcnow() + relativedelta(days=56)).date()
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose_quantity', form_validator._errors)

    def test_second_dose(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        VaccinationDetails.objects.create(
            subject_visit=self.visit_1070,
            report_datetime=(get_utcnow() + relativedelta(days=56)).date(),
            received_dose_before=SECOND_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '2',
            'dose1_product_name': 'azd_1222',
            'dose1_date': get_utcnow().date(),
            'dose2_product_name': 'azd_1',
            'dose2_date': (get_utcnow() + relativedelta(days=56)).date()
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose2_product_name', form_validator._errors)

    def test_second_dose_date(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        VaccinationDetails.objects.create(
            subject_visit=self.visit_1070,
            report_datetime=(get_utcnow() + relativedelta(days=56)).date(),
            received_dose_before=SECOND_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '2',
            'dose1_product_name': 'azd_1222',
            'dose1_date': get_utcnow().date(),
            'dose2_product_name': 'azd_1222',
            'dose2_date': (get_utcnow() + relativedelta(days=66)).date()
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose2_date', form_validator._errors)
