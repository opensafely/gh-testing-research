from ehrql import codelist_from_csv, create_dataset
from ehrql.tables.core import clinical_events, medications
from ehrql.tables.tpp import addresses, patients, practice_registrations

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
# Diastolic arterial pressure. Corresponds to CTV3 "246A."
diastolic_blood_pressure_codes = ["1091811000000102"]

dataset = create_dataset()

has_registration = practice_registrations.spanning(
    "2019-02-01", "2020-02-01"
).exists_for_patient()

dataset.define_population(has_registration)

# https://github.com/opensafely/risk-factors-research/issues/49
dataset.age = patients.age_on("2020-02-01")

# https://github.com/opensafely/risk-factors-research/issues/46
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

# https://github.com/opensafely/risk-factors-research/issues/48
bp_dias_clinical_events = clinical_events.where(
    clinical_events.snomedct_code.is_in(diastolic_blood_pressure_codes)
)
date_of_most_recent_bp_dias_clinical_event = (
    bp_dias_clinical_events.where(clinical_events.date.is_on_or_before("2020-02-01"))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)
dataset.bp_dias = bp_dias_clinical_events.where(
    clinical_events.date == date_of_most_recent_bp_dias_clinical_event
).numeric_value.mean_for_patient()

# https://github.com/opensafely/risk-factors-research/issues/44
dataset.stp = practice_registrations.for_patient_on("2020-02-01").practice_stp

# https://github.com/opensafely/risk-factors-research/issues/44
dataset.msoa = addresses.for_patient_on("2020-02-01").msoa_code

# https://github.com/opensafely/risk-factors-research/issues/45
dataset.imd = addresses.for_patient_on("2020-02-01").imd_rounded

# https://github.com/opensafely/risk-factors-research/issues/47
dataset.rural_urban = addresses.for_patient_on("2020-02-01").rural_urban_classification

dataset.recent_salbutamol_count = (
    medications.where(medications.dmd_code.is_in(salbutamol_codes))
    .where(medications.date.is_on_or_between("2018-02-01", "2020-02-01"))
    .count_for_patient()
)
