from django.apps import apps as django_apps
from edc_constants.constants import OTHER, YES, NO
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

        self.validate_other_specify(field='contraceptive')

        self.m2m_other_specify(OTHER,
                            m2m_field='contraceptive',
                            field_other='contraceptive_other',)

        self.validate_other_specify(field='post_menopausal')

        self.required_if(NO,field='amenorrhea_history',field_required='start_date_menstrual_period')
        
        self.required_if(YES,field='amenorrhea_history',field_required='expected_delivery',inverse=False)
        super().clean()
