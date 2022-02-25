from django import forms
from django.apps import apps as django_apps
from edc_constants.constants import OTHER, NO, YES
from edc_form_validators import FormValidator

from .crf_form_validator import CRFFormValidator


class PregnancyStatusFormValidator(CRFFormValidator, FormValidator):

    subject_consent_model = 'esr21_subject.informedconsent'

    @property
    def subject_consent_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    def clean(self):

        self.m2m_required_if(YES,
                             field='contraceptive_usage',
                             m2m_field='contraceptive')

        spontaneous_miscarriages = self.cleaned_data.get('number_miscarriages') or 0

        self.required_if_true(spontaneous_miscarriages > 0,
                              field_required='date_miscarriages',)

        self.m2m_other_specify(OTHER,
                               m2m_field='contraceptive',
                               field_other='contraceptive_other',)

        self.validate_other_specify(field='post_menopausal')

        amenorrhea_history = self.cleaned_data.get('amenorrhea_history')
        primary_amenorrhea = self.cleaned_data.get('primary_amenorrhea')

        self.required_if_true(
            (amenorrhea_history == NO and primary_amenorrhea == NO),
            field_required='start_date_menstrual_period')

        start_date_menstrual_period = self.cleaned_data.get('start_date_menstrual_period')
        expected_delivery = self.cleaned_data.get('expected_delivery')

        if start_date_menstrual_period and expected_delivery:
            if start_date_menstrual_period == expected_delivery:
                msg = 'Start date of menstrual period cannot be the same as date of'\
                    ' expected delivery'
                raise forms.ValidationError(msg)

        super().clean()
