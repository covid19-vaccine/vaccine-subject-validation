from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import tag
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import YES, MALE, FEMALE, OTHER

from ..form_validators import InformedConsentFormValidator
from .models import EligibilityConfirmation, InformedConsent


class TestSubjectConsentForm(TestCase):

    def setUp(self):
        InformedConsentFormValidator.eligibility_confirmation_model = \
            'esr21_subject_validation.eligibilityconfirmation'    
            
        informed_consent_model = 'esr21_subject_validation.informedconsent'

        InformedConsentFormValidator.informed_consent_model = informed_consent_model

        InformedConsentFormValidator.consent_model = \
            'esr21_subject_validation.informedconsent'

        self.eligibility_confirmation = EligibilityConfirmation.objects.create(
            report_datetime=get_utcnow(),
            age_in_years=45)
        
        InformedConsent.objects.create(
            screening_identifier=eligibility_confirmation.screening_identifier,
            subject_identifier='123-9871',
            dob = (get_utcnow() - relativedelta(years=45)).date()
        )  

        self.consent_options = {
            'screening_identifier': self.eligibility_confirmation.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 1,
            'dob': (get_utcnow() - relativedelta(years=45)).date(),
            'first_name': 'TEST ONE',
            'last_name': 'TEST',
            'initials': 'TOT',
            'identity': '123425678',
            'confirm_identity': '123425678',
            'identity_type': 'national_identity_card',
            'gender': FEMALE,
            'citizen': YES}

    @tag('re-consent')
    def test_reconsent_dob_match_consent_dob_years(self):
        v1_consent_options = {
            'screening_identifier': self.eligibility_confirmation.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 1,
            'dob': (get_utcnow() - relativedelta(years=44, months=2)).date(),
            'identity': '123425678',
            'confirm_identity': '123425678',
            'gender': FEMALE,
            'is_literate': YES,
            }
        v1_consent = InformedConsent(**v1_consent_options)
        v1_consent.save()

        consent_options = {
            'screening_identifier': v1_consent.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 3,
            'dob': (get_utcnow() - relativedelta(years=44, months=2)).date(),
            'identity': '123425678',
            'confirm_identity': '123425678',
            'gender': FEMALE,
            'is_literate': YES,
            'subject_identifier': v1_consent.subject_identifier,
        }

        form_validator = InformedConsentFormValidator(
            cleaned_data=consent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('re-consent_2')
    def test_reconsent_dob_mismatch_consent_dob_years(self):
        v1_consent_options = {
            'screening_identifier': self.eligibility_confirmation.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 1,
            'dob': (get_utcnow() - relativedelta(years=44, months=2)).date(),
            'identity': '123425678',
            'confirm_identity': '123425678',
            'gender': FEMALE,
            'is_literate': YES,
            }
        v1_consent = InformedConsent(**v1_consent_options)
        v1_consent.save()

        consent_options = {
            'screening_identifier': v1_consent.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 3,
            'dob': (get_utcnow() - relativedelta(years=45, months=2)).date(),
            'identity': '123425678',
            'confirm_identity': '123425678',
            'gender': FEMALE,
            'is_literate': YES,
            'subject_identifier': v1_consent.subject_identifier,
        }

        form_validator = InformedConsentFormValidator(
            cleaned_data=consent_options)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dob', form_validator._errors)

    def test_consent_dob_match_consent_dob_years(self):
        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
            
    def test_eligibility_age_not_valid(self):
        InformedConsent.objects.all().delete()
        
        self.consent_options['dob'] = (get_utcnow() - relativedelta(years=46)).date()

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dob', form_validator._errors)

    def test_consent_dob_mismatch_consent_dob_years(self):
        self.consent_options['dob'] = (get_utcnow() - relativedelta(years=40)).date()

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dob', form_validator._errors)

    def test_consent_gender_identity_invalid(self):
        self.consent_options['gender'] = MALE

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('identity', form_validator._errors)

    def test_consent_gender_other_specify(self):
        self.consent_options['gender'] = OTHER

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('gender_other', form_validator._errors)

    def test_consent_gender_other_provided(self):
        self.consent_options['gender'] = OTHER
        self.consent_options['gender_other'] = 'Both'

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_consent_identity_numbers_invalid(self):
        self.consent_options['identity'] = 'abcdgts'
        self.consent_options['confirm_identity'] = 'abcdgts'

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('identity', form_validator._errors)

    def test_consent_identity_omang_numbers_invalid(self):
        self.consent_options['identity'] = '123256'
        self.consent_options['confirm_identity'] = '123256'

        form_validator = InformedConsentFormValidator(
            cleaned_data=self.consent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('identity', form_validator._errors)


    