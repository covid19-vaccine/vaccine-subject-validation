from ast import If
from dateutil.relativedelta import relativedelta
from edc_constants.choices import YES
from edc_form_validators import FormValidator
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, POS, NEG, IND
from edc_base.utils import get_utcnow

class RapidHivTestingFormValidator(FormValidator):

    def clean(self):
        super().clean()
        
        self.validate_prev_test_date_valid()
        # self.applicable_if(
        #     YES,
        #     field='hiv_testing_consent',
        #     field_applicable='prev_hiv_test',)
        

        # self.not_required_if(
        #     NO,
        #     field='hiv_testing_consent',
        #     field_required='rapid_test_done',
        #     inverse=False
        # )

        prev_hiv_fields = ['hiv_test_date', 'hiv_result', 'evidence_hiv_status']

        for field in prev_hiv_fields:
            self.required_if(
                YES,
                field='prev_hiv_test',
                field_required=field
            )

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='rapid_test_date')
        
        # rapid_test_date = self.cleaned_data.get('rapid_test_date')
        # self.required_if_true(rapid_test_date is not None,
        #                       field_required='rapid_test_result')

        # self.required_if(
        #     YES,
        #     field='rapid_test_done',
        #     field_required='rapid_test_result')

        if (self.cleaned_data.get('hiv_result') and self.cleaned_data.get('hiv_result') != POS
                and self.cleaned_data.get('rapid_test_done') != YES):
            message = {'rapid_test_done': 'Rapid test must be performed '}
            raise ValidationError(message)
        # elif (self.cleaned_data.get('hiv_result') and self.cleaned_data.get('hiv_result') == POS
        #         and self.cleaned_data.get('rapid_test_done') == YES):
        #     message = {'rapid_test_done': 'Participant is HIV positive, rapid test is not required'}
        #     raise ValidationError(message)
        
        # if (self.cleaned_data.get('prev_hiv_test') == NO
        #         and self.cleaned_data.get('rapid_test_done') == NO):
        #     message = {'rapid_test_done': 'Rapid test must be performed if participant has no '
        #                                 'previous hiv results.'}
        #     raise ValidationError(message)
        
        # validate if not consented check the previous test result if they are >3months make the test required
    def validate_prev_test_date_valid(self):
        consent = self.cleaned_data.get('hiv_testing_consent')
        prev_hiv_test = self.cleaned_data.get('prev_hiv_test')
        prev_test_date = self.cleaned_data.get('hiv_test_date')
        rapid_test_done = self.cleaned_data.get('rapid_test_done')
        hiv_result = self.cleaned_data.get('hiv_result')
        rapid_test_date = self.cleaned_data.get('rapid_test_date')
        rapid_test_result = self.cleaned_data.get('rapid_test_result')
        evidence_hiv_status = self.cleaned_data.get('evidence_hiv_status')
        
        threshold_date = (get_utcnow() - relativedelta(months=3)).date()
 
        if ((consent == NO )and (prev_hiv_test == YES)):
            # check date and if it is greater thatn 3months make the rapid test required
            if prev_test_date and prev_test_date is not None:
                if evidence_hiv_status != YES:
                    message = {'prev_hiv_test': 'Cannot proceed without the interviewer seeing evidence of the HIV result?'}
                    raise ValidationError(message) 
                else:
                    
                    if rapid_test_done != YES:
                        # self.required_if_true((prev_test_date < threshold_date ),
                        # field_required='rapid_test_done') 
                        if prev_test_date < threshold_date :
                            if (hiv_result and hiv_result == POS):
                                if (rapid_test_done and rapid_test_done == YES):
                                    message = {'rapid_test_done': 'Participant is HIV positive, rapid test is not required'}
                                    raise ValidationError(message)  
                                
                            message = {'rapid_test_done': 'The previous hiv test has expired a new test is required'}
                            raise ValidationError(message)
            
            elif prev_test_date is None:
                    message = {'hiv_test_date': (
                        'HIV test date cannot be left blank.')}
                    self._errors.update(message)
                    raise ValidationError(message)      
            
        elif ((consent == YES )and (prev_hiv_test == NO)):
            if rapid_test_done and rapid_test_done == YES:
                if rapid_test_date is not None and rapid_test_date:
                    if rapid_test_result is None:
                        message = {'rapid_test_result': 'A test result is required'}
                        raise ValidationError(message)
                elif rapid_test_date is None:
                    message = {'rapid_test_date': 'The test date is required'}
                    raise ValidationError(message)     
        elif ((consent == NO )and (prev_hiv_test == NO)):
            message = {'rapid_test_result': 'The participant cannot proceed without a previous test or consenting'}
            raise ValidationError(message)
                         
                  
              
                    
                    
                        
                    
            
            
            
            
               
        
        
    