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

dataset.recent_salbutamol_count = (
    medications.where(medications.dmd_code.is_in(salbutamol_codes))
    .where(medications.date.is_on_or_between("2018-02-01", "2020-02-01"))
    .count_for_patient()
)
