from datetime import datetime, timedelta

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator

from .crf_form_validator import CRFFormValidator
from ..constants import FIRST_DOSE, SECOND_DOSE


class VaccineDetailsFormValidator(CRFFormValidator, FormValidator):
    edc_protocol = django_apps.get_app_config('edc_protocol')

    vaccination_details_cls = 'esr21_subject.vaccinationdetails'
    vaccination_history_cls = 'esr21_subject.vaccinationhistory'

    @property
    def vaccination_details_model_cls(self):
        return django_apps.get_model(self.vaccination_details_cls)

    @property
    def vaccination_history_model_cls(self):
        return django_apps.get_model(self.vaccination_history_cls)

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
        Validate second dose vaccination datetime not before first dose
        datetime, and not before 56days window period.
        """
        subject_identifier = self.cleaned_data.get('subject_visit').subject_identifier

        current_schedule = self.cleaned_data.get(
            'subject_visit').appointment.schedule_name
        schedule_names = ['esr21_fu_schedule', 'esr21_sub_fu_schedule']
        vaccination_history = self.vaccination_history_model_obj(
            subject_identifier=subject_identifier)
        if current_schedule not in schedule_names:
            if getattr(vaccination_history, 'received_vaccine', None) == NO:
                self.validate_second_dose_dt(subject_identifier=subject_identifier)
        else:
            self.validate_second_dose_dt(subject_identifier=subject_identifier)

    def validate_second_dose_dt(self, subject_identifier=None):
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
                           'Please capture the first dose vaccination details, '
                           'before second dose vaccination.'}
                raise ValidationError(msg)
            pass
        else:
            return vaccination

        self.validate_consent_date()

    def vaccination_history_model_obj(self, subject_identifier=None):
        try:
            vaccination_history = self.vaccination_history_model_cls.objects.get(
                subject_identifier=subject_identifier)
        except self.vaccination_history_model_cls.DoesNotExist:
            return None
        else:
            return vaccination_history

    def validate_vaccination_date_against_consent_date(self):
        report_datetime = self.cleaned_data.get('subject_visit').report_datetime
        vaccination_date = self.cleaned_data.get('vaccination_date')

        if vaccination_date < report_datetime:
            message = {'vaccination_date':
                           ('Vaccination date cannot be before visit report date.'
                            f' {report_datetime}.')}
            raise ValidationError(message)

    def validate_first_dose_against_second_dose(self):
        current_dose = self.cleaned_data.get('received_dose_before')
        subject_identifier = self.cleaned_data.get('subject_visit').subject_identifier
        current_schedule = self.cleaned_data.get(
            'subject_visit').appointment.schedule_name
        schedule_names = ['esr21_fu_schedule', 'esr21_sub_fu_schedule']

        if current_schedule in schedule_names:
            if current_dose == 'second_dose':
                try:
                    self.vaccination_details_model_cls.objects.get(
                        subject_visit__subject_identifier=subject_identifier,
                        received_dose_before='first_dose')
                except self.vaccination_details_model_cls.DoesNotExist:
                    message = f'Vaccination details for the first dose do not exist'
                    raise ValidationError(message)

    def validate_expiry_dt_against_visit_dt(self):
        report_datetime = self.cleaned_data.get('subject_visit').report_datetime
        expiry_date = self.cleaned_data.get('expiry_date')

        report_dt = report_datetime.date()
        if expiry_date < report_dt:
            message = {'expiry_date':
                           f'Expiry date cannot be before the visit date. {report_dt}.'}
            raise ValidationError(message)

    def validate_next_vaccination_dt_against_visit_date(self):
        report_datetime = self.cleaned_data.get('subject_visit').report_datetime
        next_vaccination_dt = self.cleaned_data.get('next_vaccination_date')

        if next_vaccination_dt:
            report_dt = report_datetime.date()
            if next_vaccination_dt < report_dt:
                message = {'next_vaccination_date':
                               ('Vaccination date cannot be before the visit report'
                                f' date. {report_datetime}.')}
                raise ValidationError(message)

    # def validate_vial_10_injections(self):
    #     """
    #     Raise an error if more than 10 forms have the same kit serial number
    #     """
    #     kit_serial_field_val = self.cleaned_data.get('kit_serial')
    #     try:
    #         total_forms = self.vaccination_details_model_cls.objects.filter(
    #             kit_serial=kit_serial_field_val
    #         ).count()
    #     except self.vaccination_details_model_cls.DoesNotExist:
    #         pass
    #     else:
    #         if total_forms == 10:
    #             message = {'kit_serial': (
    #                 f'More than 10 people have been vaccinated from vial '
    #                 f'{kit_serial_field_val}')
    #             }
    #             raise ValidationError(message)
    #
    # def validate_vial_expiration(self):
    #     """
    #     Raise an error if the oldest and the current forms of the same kit serial number
    #     are more than 6 hours apart
    #     """
    #     kit_serial_field_val = self.cleaned_data.get('kit_serial')
    #     last_vac = self.vaccination_details_model_cls.objects.filter(
    #         kit_serial=kit_serial_field_val
    #     ).order_by('report_datetime').first()
    #     time_threshold = datetime.now() - timedelta(hours=6)
    #     import pdb;
    #     pdb.set_trace()
    #     if last_vac and (last_vac.report_datetime.time() > time_threshold.time()):
    #         message = {'kit_serial': (
    #             f'Participant can not receive drug from vial of serial kit'
    #             f'{kit_serial_field_val}, this drug was first punctured more than 6 '
    #             f'hours ago')
    #         }
    #         raise ValidationError(message)
