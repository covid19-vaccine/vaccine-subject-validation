from django.forms import ValidationError
from edc_constants.constants import YES
from edc_form_validators import FormValidator


class VaccinationHistoryFormValidator(FormValidator):

    def clean(self):

        self.required_if(
            YES,
            field='received_vaccine',
            field_required='dose_quantity', )

        dose1_required = ['dose1_product_name', 'dose1_date']
        dose_quantity = self.cleaned_data.get('dose_quantity')

        for dose1_field in dose1_required:
            self.required_if_true(
                dose_quantity in ['1', '2'],
                field_required=dose1_field)

        fields_other = {'dose1_product_name': 'dose1_product_other',
                        'dose2_product_name': 'dose2_product_other'}

        for field, field_other in fields_other.items():
            self.validate_other_specify(
                field=field,
                other_specify_field=field_other)

        dose2_required = ['dose2_product_name', 'dose2_date']

        for dose2_field in dose2_required:
            self.required_if(
                '2',
                field='dose_quantity',
                field_required=dose2_field)
        if 'janssen' == self.cleaned_data['dose1_product_name'] and\
                self.cleaned_data['dose2_product_name']:
            message = {
                'dose2_product_name':
                    'Participant has received Johnson & Johnson and '
                    f"{ self.cleaned_data['dose2_product_name']} therefore "
                    'they are not eligible to participate'
            }
            raise ValidationError(message)

        if 'janssen' == self.cleaned_data['dose2_product_name'] and\
                self.cleaned_data['dose1_product_name']:
            message = {
                'dose1_product_name':
                    'Participant has received Johnson & Johnson and '
                    f"{ self.cleaned_data['dose1_product_name']} therefore "
                    'they are not eligible to participate'
            }
            raise ValidationError(message)
