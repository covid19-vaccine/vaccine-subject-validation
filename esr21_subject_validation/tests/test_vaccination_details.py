from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import NO, YES, OTHER, NOT_APPLICABLE

from ..form_validators import VaccineDetailsFormValidator
from ..constants import BOOSTER_DOSE, FIRST_DOSE, SECOND_DOSE

from .models import Appointment, SubjectVisit, VaccinationDetails, VaccinationHistory
from django.test.utils import tag

class VaccinationDetailsFormValidatorTests(TestCase):

    def setUp(self):
        self.subject_identifier = '1234567'
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000',
            schedule_name='esr21_enrol_schedule')

        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            schedule_name='esr21_enrol_schedule')
        
        vaccination_history_cls = 'esr21_subject_validation.vaccinationhistory'
        vaccination_details_cls = 'esr21_subject_validation.vaccinationdetails'

        VaccineDetailsFormValidator.vaccination_details_cls = vaccination_details_cls
        VaccineDetailsFormValidator.vaccination_history_cls = vaccination_history_cls

        self.appt_1070 = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1070',
            schedule_name='esr21_fu_schedule',
            appt_datetime=get_utcnow())

        self.visit_1070 = SubjectVisit.objects.create(
            appointment=self.appt_1070,
            schedule_name='esr21_fu_schedule')

        VaccinationDetails.objects.create(
            subject_visit=subject_visit,
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())
        
        VaccinationHistory.objects.create(
            report_datetime= get_utcnow(),
            subject_identifier=self.subject_identifier,
            received_vaccine=YES,
            dose_quantity='1',
            dose1_product_name='janssen')

        self.data = {
            'subject_visit': subject_visit,
            'received_dose': YES,
            'report_datetime': get_utcnow(),
            'received_dose_before': 'ABC',
            'vaccination_site': 'ABC',
            'vaccination_date': get_utcnow(),
            'admin_per_protocol': YES,
            'reason_not_per_protocol': None,
            'lot_number': '123',
            'expiry_date': get_utcnow() + relativedelta(days=30),
            'provider_name': 'SPA',
            'location': 'Arm',
            'location_other': None,
            'next_vaccination_date': (get_utcnow() + relativedelta(days=56)).date(),

        }

    def test_is_received_dose_required(self):
        field_name = 'received_dose_before'

        self.data[field_name] = NOT_APPLICABLE

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_vaccination_site_required(self):
        field_name = 'vaccination_site'
        self.data[field_name] = None

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_vaccination_date_required(self):
        field_name = 'vaccination_date'
        self.data[field_name] = None

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_admin_per_protocol_required(self):
        field_name = 'admin_per_protocol'

        self.data[field_name] = NOT_APPLICABLE

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_reason_not_per_protocol_required(self):
        field_name = 'reason_not_per_protocol'
        self.data[field_name] = None
        self.data['admin_per_protocol'] = NO

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_lot_number_required(self):
        field_name = 'lot_number'

        self.data[field_name] = None

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_expiry_date_required(self):
        field_name = 'expiry_date'

        self.data[field_name] = None

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_provider_name_required(self):
        field_name = 'provider_name'

        self.data[field_name] = None

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_location_required(self):
        field_name = 'location'

        self.data[field_name] = NOT_APPLICABLE

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('location', form_validator._errors)

    def test_location_other_required(self):
        field_name = 'location'

        self.data[field_name] = OTHER

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('location_other', form_validator._errors)

    def test_next_vaccination_required(self):
        field_name = 'received_dose_before'

        self.data[field_name] = FIRST_DOSE
        self.data['next_vaccination_date'] = None

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('next_vaccination_date', form_validator._errors)

    def test_next_vaccination_before_window(self):
        field_name = 'next_vaccination_date'

        self.data['received_dose_before'] = FIRST_DOSE
        self.data[field_name] = (get_utcnow() + relativedelta(days=55)).date()

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('next_vaccination_date', form_validator._errors)

    def test_second_dose_dt_before_first(self):

        self.data['received_dose_before'] = SECOND_DOSE
        self.data['vaccination_date'] = get_utcnow() - relativedelta(days=1)
        self.data['next_vaccination_date'] = None

        self.data['subject_visit'] = self.visit_1070

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('vaccination_date', form_validator._errors)

    def test_second_dose_dt_before_window(self):

        self.data['received_dose_before'] = SECOND_DOSE
        self.data['vaccination_date'] = get_utcnow() + relativedelta(days=55)
        self.data['next_vaccination_date'] = None

        self.data['subject_visit'] = self.visit_1070

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('vaccination_date', form_validator._errors)

    def test_second_dose_within_ranges(self):
        self.data['received_dose_before'] = SECOND_DOSE
        self.data['vaccination_date'] = get_utcnow() + relativedelta(days=58)
        self.data['next_vaccination_date'] = None

        self.data['subject_visit'] = self.visit_1070
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=1)).date()

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_first_dose_against_second_dose(self):
        self.data['vaccination_date'] = get_utcnow() + relativedelta(days=1)

        appt = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1000',
            schedule_name='esr21_enrol_schedule',
            appt_datetime=get_utcnow())

        visit = SubjectVisit.objects.create(
            appointment=appt,
            schedule_name='esr21_fu_schedule',
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow())

        self.data['subject_visit'] = visit
        self.data['received_dose_before'] = FIRST_DOSE
        self.data['report_datetime'] = get_utcnow()
        self.data['next_vaccination_date'] = (
                    get_utcnow() + relativedelta(days=57)).date()
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=1)).date()

        form = VaccineDetailsFormValidator(cleaned_data=self.data)
        try:
            form.validate()
        except ValidationError as e:
            self.fail(f'Received Dose Before unexpectedly raised. Got{e}')

    def test_validate_vaccination_date_against_consent_date(self):
        self.data['received_dose_before'] = FIRST_DOSE

        appt = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1000',
            schedule_name='esr21_enrol_schedule',
            appt_datetime=get_utcnow())

        visit = SubjectVisit.objects.create(
            appointment=appt,
            schedule_name='esr21_enrol_schedule',
            report_datetime=get_utcnow())

        self.data['next_vaccination_date'] = (
                    get_utcnow() + relativedelta(days=57)).date()

        self.data['subject_visit'] = visit
        self.data['report_datetime'] = get_utcnow()
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=1)).date()

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('vaccination_date', form_validator._errors)
     
    def test_validate_expiry_dt_against_visit_dt(self):

        field_name = 'expiry_date'
        self.data['next_vaccination_date'] = None

        appt = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1000',
            schedule_name='esr21_enrol_schedule',
            appt_datetime=get_utcnow())

        visit = SubjectVisit.objects.create(
            appointment=appt,
            schedule_name='esr21_enrol_schedule',
            report_datetime=get_utcnow())

        self.data['vaccination_date'] = get_utcnow()
        self.data['subject_visit'] = visit
        self.data['report_datetime'] = get_utcnow()
        self.data['expiry_date'] = (get_utcnow() - relativedelta(days=1)).date()

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)
    
     
    def test_validate_next_vaccination_dt_against_visit_date(self):
        field_name = 'next_vaccination_date'

        self.data['received_dose_before'] = FIRST_DOSE
        self.data['next_vaccination_date'] = (
                    get_utcnow() + relativedelta(days=55)).date()

        appt = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1000',
            schedule_name='esr21_enrol_schedule',
            appt_datetime=get_utcnow())

        visit = SubjectVisit.objects.create(
            appointment=appt,
            schedule_name='esr21_enrol_schedule',
            report_datetime=get_utcnow())

        self.data['subject_visit'] = visit
        self.data['report_datetime'] = get_utcnow()
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=50)).date()

        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)
             
 
    def test_vac_hist_against_sec_dose_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000',
            schedule_name='esr21_enrol_schedule')
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            schedule_name='esr21_enrol_schedule')
        
        VaccinationDetails.objects.create(
            report_datetime= get_utcnow(),
            subject_visit=subject_visit,
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())
         
        VaccinationHistory.objects.create(
            report_datetime= get_utcnow(),
            subject_identifier=self.subject_identifier,
            received_vaccine=YES,
            dose_quantity='1')
        
        self.data['received_dose_before'] = SECOND_DOSE
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=30)).date()
        form = VaccineDetailsFormValidator(cleaned_data=self.data)
        try:
            form.validate()
        except ValidationError as e:
            self.fail(f'Received Dose Before unexpectedly raised. Got{e}')

    def test_vac_hist_against_booster_dose_valid(self):
         
        VaccinationHistory.objects.create(
            report_datetime= get_utcnow(),
            subject_identifier=self.subject_identifier,
            received_vaccine=YES,
            dose_quantity='2')
        
        self.data['received_dose_before'] = BOOSTER_DOSE
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=30)).date()
        self.data['next_vaccination_date'] = None
        form = VaccineDetailsFormValidator(cleaned_data=self.data)
        try:
            form.validate()
        except ValidationError as e:
            self.fail(f'Received Dose Before unexpectedly raised. Got{e}')


    def test_vac_hist_against_sec_dose_invalid(self):
         
        VaccinationHistory.objects.create(
            report_datetime= get_utcnow(),
            subject_identifier=self.subject_identifier,
            received_vaccine=YES,
            dose_quantity='1')
        
        self.data['received_dose_before'] = FIRST_DOSE
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=30)).date()


        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('received_dose_before', form_validator._errors)
        
    def test_vac_hist_against_booster_dose_invalid(self):
         
        VaccinationHistory.objects.create(
            report_datetime= get_utcnow(),
            subject_identifier=self.subject_identifier,
            received_vaccine=YES,
            dose_quantity='2')
        
        self.data['received_dose_before'] = FIRST_DOSE
        self.data['expiry_date'] = (get_utcnow() + relativedelta(days=30)).date()


        form_validator = VaccineDetailsFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('received_dose_before', form_validator._errors)
