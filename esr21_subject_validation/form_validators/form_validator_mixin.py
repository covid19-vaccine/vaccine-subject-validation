from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError


class ESR21FormValidatorMixin:

    eligibility_confirmation_model = 'esr21_subject.eligibilityconfirmation'
    informed_consent_model = 'esr21_subject.informedconsent'
    vaccine_details_model = 'esr21_subject.vaccinedetails'

    @property
    def eligibility_confirmation_cls(self):
        return django_apps.get_model(self.eligibility_confirmation_model)

    @property
    def informed_consent_cls(self):
        return django_apps.get_model(self.informed_consent_model)

    @property
    def vaccine_details_cls(self):
        return django_apps.get_model(self.vaccine_details_model)

    def validate_against_consent_datetime(self, report_datetime):
        """Returns an instance of the current informed consent or
        raises an exception if not found."""

        consent = self.validate_against_consent(id=id)

        if report_datetime and report_datetime < consent.consent_datetime:
            raise forms.ValidationError(
                "Report datetime cannot be before consent datetime")

    def validate_against_consent(self):
        """Returns an instance of the current inofrmed consent version form or
        raises an exception if not found."""
        consent = self.informed_consent_cls.objects.filter(
            subject_identifier=self.subject_identifier).order_by(
                '-consent_datetime').first()

        if not consent:
            raise ValidationError(
                'Please complete Informed Consent form '
                f'before  proceeding.')
        return consent
