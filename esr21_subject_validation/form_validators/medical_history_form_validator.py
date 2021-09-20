import pdb
from django import forms
from django.forms.models import BaseInlineFormSet
from edc_constants.constants import YES, OTHER
from edc_form_validators import FormValidator
from esr21_subject.models import medical_history
from .crf_form_validator import CRFFormValidator
from django.forms import ValidationError
from django.apps import apps as django_apps




class MedicalHistoryFormValidator(CRFFormValidator, FormValidator):

    medical_diagnosis = 'esr21_subject.medicaldiagnosis'

    @property
    def medical_diagnosis_cls(self):
        return django_apps.get_model(self.medical_diagnosis)

    def clean(self):
        self.m2m_required_if(YES,
                            field='prior_covid_infection',
                            m2m_field='covid_symptoms')

        self.m2m_other_specify(OTHER,
                            m2m_field='covid_symptoms',
                            field_other='symptoms_other')

        self.m2m_other_specify(OTHER,
                            m2m_field='comorbidities',
                            field_other='comorbidities_other')

        relevant_history = self.cleaned_data['relevant_history']

        super().clean()
        
        # if relevant_history == YES:
        #     medical_diagnosis = self.medical_diagnosis_cls.objects.filter(medical_history=self.instance)
        #     if medical_diagnosis.count() == 0:
        #         msg = 'Subject have relevant medical history, '\
        #         f'{self.medical_diagnosis_cls._meta.verbose_name} is required'
        #         raise forms.ValidationError(msg)
        
