from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import NO, YES, OTHER, NOT_APPLICABLE

from ..form_validators import VaccineDetailsFormValidator
from ..constants import FIRST_DOSE

from .models import Appointment, SubjectVisit
from django.test.utils import tag


class VaccinationDetailsFormValidatorTests(TestCase):

    def setUp(self):
        subject_identifier = '1234567'
        appointment = Appointment.objects.create(
            subject_identifier=subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000',
            schedule_name='esr21_enrol_schedule')
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            schedule_name='esr21_enrol_schedule')
        self.data = {
            'subject_visit': subject_visit,
            'received_dose': YES,
            'report_datetime': get_utcnow().date(),
            'received_dose_before': 'ABC',
            'vaccination_site': 'ABC',
            'vaccination_date': 'ABC',
            'admin_per_protocol': YES,
            'reason_not_per_protocol': None,
            'lot_number': '123',
            'expiry_date': '01/01/2023',
            'provider_name': 'SPA',
            'location': 'Arm',
            'location_other': None,
            'next_vaccination_date': 'ABSC',

        }

    def test_is_received_dose_required(self):
        field_name = 'received_dose_before'

        self.data[field_name] = NOT_APPLICABLE

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_vaccination_site_required(self):
        field_name = 'vaccination_site'
        self.data[field_name] = None

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_vaccination_date_required(self):
        field_name = 'vaccination_date'
        self.data[field_name] = None

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_admin_per_protocol_required(self):
        field_name = 'admin_per_protocol'

        self.data[field_name] = NOT_APPLICABLE

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_reason_not_per_protocol_required(self):
        field_name = 'reason_not_per_protocol'
        self.data[field_name] = None
        self.data['admin_per_protocol'] = NO

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_lot_number_required(self):
        field_name = 'lot_number'

        self.data[field_name] = None

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_expiry_date_required(self):
        field_name = 'expiry_date'

        self.data[field_name] = None

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_provider_name_required(self):
        field_name = 'provider_name'

        self.data[field_name] = None

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn(field_name, form._errors)

    def test_location_required(self):
        field_name = 'location'

        self.data[field_name] = NOT_APPLICABLE

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn('location', form._errors)

    def test_location_other_required(self):
        field_name = 'location'

        self.data[field_name] = OTHER

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn('location_other', form._errors)

    def test_next_vaccination_required(self):
        field_name = 'received_dose_before'

        self.data[field_name] = FIRST_DOSE

        form = VaccineDetailsFormValidator(cleaned_data=self.data)

        self.assertRaises(ValidationError, form.validate)
        self.assertIn('next_vaccination_date', form._errors)
