from ehrql import codelist_from_csv, create_dataset
from ehrql.tables.core import clinical_events, medications
from ehrql.tables.tpp import patients, practice_registrations

chronic_cardiac_disease_codes = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease-snomed.csv", column="id"
)
chronic_liver_disease_codes = codelist_from_csv(
    "codelists/opensafely-chronic-liver-disease-snomed.csv", column="id"
)
salbutamol_codes = codelist_from_csv(
    "codelists/opensafely-asthma-inhaler-salbutamol-medication.csv", column="id"
)
# Systolic arterial pressure. Corresponds to CTV3 "2469."
systolic_blood_pressure_codes = ["72313002"]

dataset = create_dataset()

index_date = "2020-03-31"

has_registration = practice_registrations.for_patient_on(
    index_date
).exists_for_patient()

dataset.define_population(has_registration)

dataset.sex = patients.sex

dataset.chronic_cardiac_disease = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(chronic_cardiac_disease_codes)
    )
    .sort_by(clinical_events.date)
    .first_for_patient()
    .date
)

dataset.chronic_liver_disease = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(chronic_liver_disease_codes)
    )
    .sort_by(clinical_events.date)
    .first_for_patient()
    .date
)

# https://github.com/opensafely/risk-factors-research/issues/48
bp_sys_clinical_events = clinical_events.where(
    clinical_events.snomedct_code.is_in(systolic_blood_pressure_codes)
)
date_of_most_recent_bp_sys_clinical_event = (
    bp_sys_clinical_events.where(clinical_events.date.is_on_or_before("2020-02-01"))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)
dataset.bp_sys = bp_sys_clinical_events.where(
    clinical_events.date == date_of_most_recent_bp_sys_clinical_event
).numeric_value.mean_for_patient()

dataset.recent_salbutamol_count = (
    medications.where(medications.dmd_code.is_in(salbutamol_codes))
    .where(medications.date.is_on_or_between("2018-02-01", "2020-02-01"))
    .count_for_patient()
)
