from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel, ListModelMixin
from edc_base.utils import get_utcnow


class Appointment(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    appt_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=25)

    schedule_name = models.CharField(max_length=25)


class ListModel(ListModelMixin, BaseUuidModel):
    pass


class EligibilityConfirmation(BaseUuidModel):

    screening_identifier = models.CharField(
        max_length=36,
        unique=True,
        editable=False)

    report_datetime = models.DateTimeField(
        null=True,
        blank=True)

    age_in_years = age_in_years = models.IntegerField()


class InformedConsent(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    gender = models.CharField(max_length=10)

    is_literate = models.CharField(max_length=25,
                                   blank=True,
                                   null=True)

    witness_name = models.CharField(max_length=25,
                                    blank=True,
                                    null=True)

    dob = models.DateField()

    consent_datetime = models.DateTimeField(default=get_utcnow())

    version = models.CharField(
        max_length=10,
        editable=False)


class SubjectVisit(BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    visit_code = models.CharField(max_length=25)

    visit_code_sequence = models.IntegerField(default=0)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    schedule_name = models.CharField(max_length=25)

    def save(self, *args, **kwargs):
        self.visit_code = self.appointment.visit_code
        self.subject_identifier = self.appointment.subject_identifier
        super().save(*args, **kwargs)


class AdverseEvent(models.Model):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    serious_event = models.CharField(max_length=25, blank=True, null=True)

    special_interest_ae = models.CharField(max_length=25, blank=True, null=True)


class VaccinationDetails(models.Model):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    received_dose_before = models.CharField(max_length=25)

    vaccination_date = models.DateTimeField()

    next_vaccination_date = models.DateField()
