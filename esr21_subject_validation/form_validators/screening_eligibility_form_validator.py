

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES
from edc_form_validators import FormValidator


class ScreeningEligibilityFormValidator(FormValidator):

    edc_protocol = django_apps.get_app_config('edc_protocol')

    @property
    def screening_eligibility_cls(self):
        return django_apps.get_model(self.screening_eligibility_model)

    def clean(self):

        report_datetime = self.cleaned_data.get('report_datetime')
        if (report_datetime and self.edc_protocol.study_open_datetime > report_datetime):
            message = {
                'report_datetime': ('Date cannot be before study starts. Study opened on'
                                    f' {self.edc_protocol.study_open_datetime.date()}.')}
            self._errors.update(message)
            raise ValidationError(message)
        self.required_if(YES, field='childbearing_potential', field_required='birth_control')
        self.required_if(YES, field='birth_control', field_required='birthcontrol_agreement')
