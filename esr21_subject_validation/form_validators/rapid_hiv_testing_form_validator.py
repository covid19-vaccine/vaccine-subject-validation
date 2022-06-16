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
        
        self.validate_consent_status()

        prev_hiv_fields = ['hiv_test_date', 'hiv_result', 'evidence_hiv_status']

        for field in prev_hiv_fields:
            self.required_if(
                YES,
                field='prev_hiv_test',
                field_required=field
            )

        rapid_test_fields = ['rapid_test_date','rapid_test_result']
        for field in rapid_test_fields:
            self.required_if(
            YES,
            field='rapid_test_done',
            field_required=field)
        
       
    def validate_consent_status(self):
        """A function to validate the consent status of a participant and 
        to validate the validity of the previous test if the participant does not
        give consent
        """
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
            if prev_test_date and prev_test_date is not None:
                if evidence_hiv_status != YES:
                    message = {'prev_hiv_test': 'Cannot proceed without the interviewer seeing evidence of the HIV result?'}
                    raise ValidationError(message) 
                else:
                    
                    if rapid_test_done != YES:
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
            
        elif (consent == YES):
            if rapid_test_done != YES:
                message = {'rapid_test_done': 'A test needs to be processed'}
                raise ValidationError(message)  
            else:
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
                         
                  
              
                    
                    
                        
                    
            
            
            
            
               
        
        
    