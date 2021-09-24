from dateutil.relativedelta import relativedelta
from edc_constants.choices import YES
from edc_form_validators import FormValidator
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, POS, NEG, IND


class RapidHivTestingFormValidator(FormValidator):

    def clean(self):
        super().clean()

        rapid_test_date = self.cleaned_data.get('rapid_test_date')
        hiv_test_date = self.cleaned_data.get('hiv_test_date')
        hiv_testing_consent = self.cleaned_data.get('hiv_testing_consent')
        hiv_result = self.cleaned_data.get('hiv_result')
        prev_hiv_test = self.cleaned_data.get('prev_hiv_test')

        self.applicable_if(
            YES,
            field='hiv_testing_consent',
            field_applicable='prev_hiv_test',)
        

        self.not_required_if(
            NO,
            field='hiv_testing_consent',
            field_required='rapid_test_done',
            inverse=False
        )

        prev_hiv_fields = ['hiv_test_date', 'hiv_result', 'evidence_hiv_status']

        for field in prev_hiv_fields:
            self.required_if(
                YES,
                field='prev_hiv_test',
                field_required=field
            )

        # self.applicable_if_true(
        #     hiv_testing_consent==YES and prev_hiv_test == NO or hiv_result in [NEG, IND],
        #     field_applicable='rapid_test_done',
        # )

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='rapid_test_date')

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='rapid_test_result')

        # self.not_required_if(
        #     POS,
        #     field='hiv_result',
        #     field_required='rapid_test_done',
        #     inverse=False
        # )

        


        # self.required_if_true(
        #     hiv_testing_consent == YES and hiv_result != POS,
        #     field_required='rapid_test_done',
        # )

        subject_visit = self.cleaned_data.get('subject_visit')

        # if hiv_test_date:

        rapid_test_done = self.cleaned_data.get('rapid_test_done')

    #     date_diff = relativedelta(subject_visit.report_datetime.date(), hiv_test_date)

        if (self.cleaned_data.get('hiv_result') and self.cleaned_data.get('hiv_result') != POS
                and self.cleaned_data.get('rapid_test_done') != YES):
            message = {'rapid_test_done': 'Rapid test must be performed '}
            raise ValidationError(message)
        elif (self.cleaned_data.get('hiv_result') and self.cleaned_data.get('hiv_result') == POS
                and self.cleaned_data.get('rapid_test_done') == YES):
            message = {'rapid_test_done': 'Participant is HIV positive, rapid test is not required'}
            raise ValidationError(message)
        
        # if rapid_test_date:

        #     date_diff = relativedelta(subject_visit.report_datetime.date(), rapid_test_date)

        #     if date_diff.years or date_diff.months >= 3:
        #         message = {'rapid_test_date': 'The date provided is more than 3 months old.'}
        #         raise ValidationError(message)

        if (self.cleaned_data.get('prev_hiv_test') == NO
                and self.cleaned_data.get('rapid_test_done') == NO):
            message = {'rapid_test_done': 'Rapid test must be performed if participant has no '
                                        'previous hiv results.'}
            raise ValidationError(message)
