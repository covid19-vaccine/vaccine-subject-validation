from edc_constants.choices import YES
from edc_constants.constants import OTHER
from edc_form_validators import FormValidator


class Covid19SymptomaticInfectionsFormValidator(FormValidator):

    def clean(self):
        super().clean()
        
        self.validate_m2m_required()
        self.validate_other_specify()
        self.validate_date_of_infection_required()
        self.validate_hospital_visit_date_required()
        
    def validate_other_specify(self):
         
        self.m2m_other_specify('OTHER',
                m2m_field='symptomatic_infections',
                field_other='symptomatic_infections_other', )
        
        
    def validate_m2m_required(self):
        self.m2m_required_if(
            YES,
            field='symptomatic_experiences',
            m2m_field='symptomatic_infections')     
    
    def validate_date_of_infection_required(self):
        self.required_if(
            YES,
            field='symptomatic_experiences',
            field_required='date_of_infection')
            
        
    def validate_hospital_visit_date_required(self):
        self.required_if(
            YES,
            field='hospitalisation_visit',
            field_required='hospitalisation_date')    
         