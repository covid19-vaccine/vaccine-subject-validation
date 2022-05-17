from django.core.exceptions import ValidationError
from edc_constants.choices import NO
from edc_constants.constants import YES
from edc_form_validators import FormValidator
from django import forms


class PhysicalFormValidator(FormValidator):
    def clean(self):
        super().clean()
        """
        2 subsequence questions are required if the physical variable is a NO
        """
        self.applicable_if(NO,
                           field='physical_exam',
                           field_applicable='reason_not_done')
        self.required_if(YES,
                         field='physical_exam',
                         field_required='exam_date')

        fields_required = ['abn_specify', 'clinically_significant']

        for field in fields_required:
            self.required_if(YES,
                             field='abnormalities_found',
                             field_required=field)

        """
        Description required if a check is abnormal
        """
        self.required_if('abnormal',
                         field='general_appearance',
                         field_required='abnormality_description')

        self.required_if('abnormal',
                         field='face_check',
                         field_required='face_description')

        self.required_if('abnormal',
                         field='neck_check',
                         field_required='neck_description')

        self.required_if('abnormal',
                         field='respiratory_check',
                         field_required='respiratory_description')

        self.required_if('abnormal',
                         field='cardiovascular_check',
                         field_required='cardiovascular_description')

        self.required_if('abnormal',
                         field='abdominal_check',
                         field_required='abdominal_description')

        self.required_if('abnormal',
                         field='skin_check',
                         field_required='skin_description')

        self.required_if('abnormal',
                         field='neurological_check',
                         field_required='neurological_description')
