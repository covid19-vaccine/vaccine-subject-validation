from bcrypt import re
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator
from .crf_form_validator import CRFFormValidator
from ..constants import FIRST_DOSE, SECOND_DOSE
from django.core.exceptions import ValidationError

class VaccineDetailsFormValidator(CRFFormValidator, FormValidator):
    edc_protocol = django_apps.get_app_config('edc_protocol')

    vaccination_details_cls = 'esr21_subject.vaccinationdetails'

    @property
    def vaccination_details_model_cls(self):
        return django_apps.get_model(self.vaccination_details_cls)

    def clean(self):
        super().clean()

        required_fields = ['vaccination_site', 'vaccination_date',
                           'lot_number', 'expiry_date', 'provider_name']

        for required_field in required_fields:
            self.required_if(YES,
                             field='received_dose',
                             field_required=required_field)

        applicable_fields = ['received_dose_before', 'location',
                             'admin_per_protocol']

        for applicable_field in applicable_fields:
            self.applicable_if(YES,
                               field='received_dose',
                               field_applicable=applicable_field)

        self.required_if(NO,
                         field='admin_per_protocol',
                         field_required='reason_not_per_protocol')

        self.validate_other_specify(field='location')
        

        self.required_if(FIRST_DOSE,
                         field='received_dose_before',
                         field_required='next_vaccination_date')

        self.validate_vaccination_date()

        self.validate_next_vaccination_dt()
        
        self.validate_first_dose_against_second_dose()
        
        self.validate_vaccination_date_against_consent_date()
        
        self.validate_expiry_dt_against_visit_dt()
        
        self.validate_next_vaccination_dt_against_visit_date()

    def validate_vaccination_date(self):
        """
        Validate second dose vaccination datetime not before first dose datetime,
        and not before 56days window period.
        """
        subject_identifier = self.cleaned_data.get('subject_visit').subject_identifier
        vaccination_datetime = self.cleaned_data.get('vaccination_date')
        dose_received = self.cleaned_data.get('received_dose_before')

        if vaccination_datetime and dose_received == SECOND_DOSE:
            second_dose_dt = vaccination_datetime.date()
            vaccination = self.vaccination_details_model_obj(
                dose_received=FIRST_DOSE, subject_identifier=subject_identifier)
            first_dose_dt = vaccination.vaccination_date.date()

            second_before_first = True if second_dose_dt < first_dose_dt else False

            difference = (second_dose_dt - first_dose_dt).days
            second_lt_window = True if difference < 56 else False

            if second_before_first or second_lt_window:
                message = {'vaccination_date':
                           'Please make sure the second dose vaccination date '
                           'is not before the first dose vaccination date or '
                           'the before the vaccination window period.'}
                raise ValidationError(message)

    def validate_next_vaccination_dt(self):
        """
        Validate next vaccination datetime is not before the vaccination window
        period.
        """
        next_vaccination_dt = self.cleaned_data.get('next_vaccination_date')
        dose_received = self.cleaned_data.get('received_dose_before')
        vaccination_datetime = self.cleaned_data.get('vaccination_date')

        if vaccination_datetime and dose_received == FIRST_DOSE:
            first_dose_dt = vaccination_datetime.date()
            date_diff = (next_vaccination_dt - first_dose_dt).days

            if date_diff < 56:
                message = {'next_vaccination_date':
                           'The next vaccination date cannot be before the '
                           'vaccination window period.'}
                raise ValidationError(message)

    def vaccination_details_model_obj(
            self, dose_received='first_dose', subject_identifier=None):
        try:
            vaccination = self.vaccination_details_model_cls.objects.get(
                subject_visit__subject_identifier=subject_identifier,
                received_dose_before=dose_received)
        except self.vaccination_details_model_cls.DoesNotExist:
            if dose_received == FIRST_DOSE:
                msg = {'received_dose_before':
                       'Please capture the first dose vaccination details, before '
                       'second dose vaccination.'}
                raise ValidationError(msg)
            pass
        else:
            return vaccination
        
        
        self.validate_consent_date()

    def validate_vaccination_date_against_consent_date(self):        
        report_datetime = self.cleaned_data.get('subject_visit').report_datetime
        vaccination_date = self.cleaned_data.get('vaccination_date')

        if vaccination_date < report_datetime:
            message = {'vaccination_date': ('Vaccination date cannot be before consent date.'
                                    f' {report_datetime}.')}
            raise ValidationError(message)

    def validate_first_dose_against_second_dose(self):  
        current_dose = self.cleaned_data.get('received_dose_before')
        subject_identifier = self.cleaned_data.get('subject_visit').subject_identifier
        current_schedule = self.cleaned_data.get('subject_visit').appointment.schedule_name
        schedule_names = ['esr21_fu_schedule','esr21_sub_fu_schedule']

        if current_schedule in schedule_names:
            if current_dose == 'second_dose':
                try:
                    self.vaccination_details_model_cls.objects.get(
                    subject_visit__subject_identifier=subject_identifier, received_dose_before = 'first_dose')              
                except self.vaccination_details_model_cls.DoesNotExist:            
                    message = f'Vaccination details for the first dose do not exist'
                    raise ValidationError(message)  
                
    def validate_expiry_dt_against_visit_dt(self):        
        report_datetime = self.cleaned_data.get('subject_visit').report_datetime
        expiry_date = self.cleaned_data.get('expiry_date')
        
        report_dt = report_datetime.date()
        if  expiry_date < report_dt:
            message = {'expiry_date': ('Expiry date cannot be before the visit date.'
                       f' {report_dt}.')}
            raise ValidationError(message)       
            
        
    def validate_next_vaccination_dt_against_visit_date(self):
        report_datetime = self.cleaned_data.get('subject_visit').report_datetime
        next_vaccination_dt = self.cleaned_data.get('next_vaccination_date')

        if next_vaccination_dt:
            report_dt = report_datetime.date()
            if next_vaccination_dt < report_dt:
                message = {'next_vaccination_date': ('Vaccination date cannot be before the visit report date.'
                            f' {report_datetime}.')}
                raise ValidationError(message) 
               
       
            