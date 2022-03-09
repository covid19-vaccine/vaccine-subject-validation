import pytz
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator
from .crf_form_validator import CRFFormValidator
from ..constants import FIRST_DOSE


class VaccineDetailsFormValidator(CRFFormValidator, FormValidator):

    def clean(self):

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

        self.validate_next_vaccination_dt()

        super().clean()

    def validate_subject_doses(self):
        """
        This is a validation which check if the vaccination is first or second
        dose
        """

        received_dose_before = self.cleaned_data.get('received_dose_before')
        subject_visit = self.cleaned_data.get('subject_visit')
        if received_dose_before == 'first_dose' and \
                subject_visit.schedule_name != 'esr21_enrol_schedule':
            # validation for second visit
            raise ValidationError(
                {'received_dose_before':
                 'This is not an enrolment visit, cannot key as a first dose'})

        if received_dose_before == 'second_dose' and \
                subject_visit.schedule_name == 'esr21_enrol_schedule':
            # validation for first visit
            raise ValidationError(
                {'received_dose_before':
                 'Should be keyed as first dose, for the enrolment visit'})

    def validate_next_vaccination_dt(self):
        next_vaccination_dt = self.cleaned_data.get('next_vaccination_date')
        appt = self.cleaned_data.get('subject_visit').appointment
        visit_code = self.cleaned_data.get('subject_visit').visit_code
        visit_definition = appt.visits.get(visit_code)

        earliest_appt_date = (self.instance.timepoint_datetime -
                              visit_definition.rlower).astimezone(
                                  pytz.timezone('Africa/Gaborone'))

        latest_appt_date = (self.instance.timepoint_datetime +
                            visit_definition.rupper).astimezone(
                                pytz.timezone('Africa/Gaborone'))

        if next_vaccination_dt:
            if (next_vaccination_dt < earliest_appt_date or
                    next_vaccination_dt > latest_appt_date):
                message = {'next_vaccination_date':
                           'The appointment date time cannot be outside the '
                           'vaccination window period'}
                raise ValidationError(message)
