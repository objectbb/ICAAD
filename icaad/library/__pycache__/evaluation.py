from enum import Enum
from pprint import pprint

class Feature:
    def __init__(self, name, values, default):
        self.name = name.lower()
        self.values = [str(x).lower() for x in values] if values is not None else None  # possible values
        self.default = str(default).lower() if default is not None else None

## evaluation types
# standard categorical - 
# standard numerical - 
# nuanced - 
# general text - 

## evaluation level (individual prompt vs feature group prompt)
# feature level
# feature group level

doc_id = "doc_id"
paclii_id = "paclii_id"
is_victim_female = "is_victim_female"
is_sentencing_decision = "is_sentencing_decision"
is_post_2000 = "is_post_2000"
is_applicable_case = "is_applicable_case"
case_type = "case_type"
date = "date"
country = "country"
city_district_of_hearing = "city_district_of_hearing" 
is_appellate_case = "is_appellate_case"
case_citation = "case_citation"
judicial_officer_name = "judicial_officer_name"
courts_jurisdiction = "courts_jurisdiction"
charges = "charges"
charge_category = "charge_category"
is_anonymity_maintained = "is_anonymity_maintained"
victim_gender = "victim_gender"
victim_age_at_offense = "victim_age_at_offense"
victim_is_adult_at_offense = "victim_is_adult_at_offense"
victim_identify_as = "victim_identify_as"
victim_disability = "victim_disability"
perpetrator_gender = "perpetrator_gender"
perpetrator_age_at_offense = "perpetrator_age_at_offense"
perpetrator_is_adult_at_offense = "perpetrator_is_adult_at_offense"
perpetrator_is_known_to_victim = "perpetrator_is_known_to_victim"
perpetrator_relationship_with_victim = "perpetrator_relationship_with_victim"
perpetrator_guilt = "perpetrator_guilt"
perpetrator_first_time_offender_case = "perpetrator_first_time_offender_case"
perpetrator_first_time_offender_self = "perpetrator_first_time_offender_self"
pathology_report = "pathology_report"
medical_report = "medical_report"
social_enquiry_report = "social_enquiry_report"
protection_order = "protection_order"
starting_sentence = "starting_sentence"
alternative_starting_sentence = "alternative_starting_sentence"
aggravating_factors = "aggravating_factors"
mitigating_factors = "mitigating_factors"
final_sentence = "final_sentence"
customary_practices = "customary_practices"
gender_stereotypes = "gender_stereotypes"
other_factors = "other_factors"
is_sole_breadwinner = "is_sole_breadwinner"
gender_discrimination_type = "gender_discrimination_type"
sentence_reduction1 = "sentence_reduction1"
sentence_reduction2 = "sentence_reduction2"
life_death_penalty = "life_death_penalty"
sentence_suspended = "sentence_suspended"
prison_sentence = "prison_sentence"
cumulative_concurrent_sentence = "cumulative_concurrent_sentence"
other_form_punishment = "other_form_punishment"
fine_bond = "fine_bond"
final_sentence_including_suspension = "final_sentence_including_suspension"
positive_judicial_statements = "positive_judicial_statements"
negative_judicial_statements = "negative_judicial_statements"
notes = "notes"

class BasicFeatureEnum(Enum):
    DOC_ID = Feature(doc_id, None, "Unknown")
    PACLII_ID = Feature(paclii_id, None, "Unknown")
    IS_VICTIM_FEMALE = Feature(is_victim_female, ["Yes", "No"], "No")
    IS_SENTENCING_DECISION = Feature(is_sentencing_decision, ["Yes", "No"], "No")
    IS_POST_2000 = Feature(is_post_2000, ["Yes", "No"], "No")
    IS_APPLICABLE_CASE = Feature(is_applicable_case, ["Yes", "No"], "No")


class CaseInfoEnum(Enum):
    CASE_TYPE = Feature(case_type, ["sexual_violence", "domestic_violence", "sexual_domestic_violence", "manslaughter_murder"], "sexual_violence")
    DATE = Feature(date, None, "Unknown")     # DD/MM/YYYY
    COUNTRY = Feature(country, None, "Unknown")   # PNG/Fiji/Samoa/Tonga
    CITY_DISTRICT_OF_HEARING = Feature(city_district_of_hearing, None, "Unknown")
    IS_APPELLATE_CASE = Feature(is_appellate_case, ["Yes", "No"], "No")
    CASE_CITATION = Feature(case_citation, None, "Unknown")     # “State v [Name of accused] [year] [name of court] [number]”
    JUDICIAL_OFFICER_NAME = Feature(judicial_officer_name, None, "Unknown")
    COURTS_JURISDICTION = Feature(courts_jurisdiction, ["Court of First Instance", "Appellate Court", "Supreme Court", "Unknown"], "Unknown")
    CHARGES = Feature(charges, None, "Unknown")
    CHARGE_CATEGORY = Feature(charge_category, None, "Unknown")
    IS_ANONYMITY_MAINTAINED = Feature(is_anonymity_maintained, ["Yes", "No", "Unknown"], "Unknown")


class VictimInfoEnum(Enum):
    VICTIM_GENDER = Feature(victim_gender, ["male", "female", "other", "Unknown"], "Unknown")
    VICTIM_AGE_AT_OFFENSE = Feature(victim_age_at_offense, None, 0)
    VICTIM_IS_ADULT_AT_OFFENSE = Feature(victim_is_adult_at_offense, ["Yes", "No", "Unknown"], "Unknown")  # DERIVED FROM ABOVE? - BUT CAN BE INFERED FROM OTHER STUFF IF AGE IS NOT GIVEN
    VICTIM_IDENTIFY_AS = Feature(victim_identify_as, None, "Unknown")    # Change to sexuality?
    VICTIM_DISABILITY = Feature(victim_disability, ["physical", "mental", "physical_mental", "no"], "no")


class PerpetratorInfoEnum(Enum):
    PERPETRATOR_GENDER = Feature(perpetrator_gender, ["male", "female", "other", "Unknown"], "Unknown")
    PERPETRATOR_AGE_AT_OFFENSE = Feature(perpetrator_age_at_offense, None, 0)
    PERPETRATOR_IS_ADULT_AT_OFFENSE = Feature(perpetrator_is_adult_at_offense, ["Yes", "No", "Unknown"], "Unknown")  # DERIVED FROM ABOVE? - BUT CAN BE INFERED FROM OTHER STUFF IF AGE IS NOT GIVEN
    PERPETRATOR_IS_KNOWN_TO_VICTIM = Feature(perpetrator_is_known_to_victim, ["Yes", "No", "Unknown"], "Unknown")
    PERPETRATOR_RELATIONSHIP_WITH_VICTIM = Feature("relationship_with_victim", None, "Unknown")
    PERPETRATOR_GUILT = Feature(perpetrator_guilt, ["plead_guilty", "found_guilty", "Unknown"], "Unknown")
    PERPETRATOR_FIRST_TIME_OFFENDER_CASE = Feature(perpetrator_first_time_offender_case, ["Yes", "No", "Unknown"], "Unknown")
    PERPETRATOR_FIRST_TIME_OFFENDER_SELF = Feature(perpetrator_first_time_offender_self, ["Agree", "Disagree"], "Agree")


class AtHearingEnum(Enum):
    PATHOLOGY_REPORT = Feature(pathology_report, ["Yes", "No"], "No")
    MEDICAL_REPORT = Feature(medical_report, ["Yes", "No"], "No")
    SOCIAL_ENQUIRY_REPORT = Feature(social_enquiry_report, ["Yes", "No"], "No")   # MISSING


class SentencingBasicEnum(Enum):
    PROTECTION_ORDER = Feature(protection_order, ["Yes", "No"], "No")
    STARTING_SENTENCE = Feature(starting_sentence, None, 0.0)
    ALTERNATIVE_STARTING_SENTENCE = Feature(alternative_starting_sentence, None, 0.0)
    AGGRAVATING_FACTORS = Feature(aggravating_factors, None, 0.0)
    MITIGATING_FACTORS = Feature(mitigating_factors, None, 0.0)
    FINAL_SENTENCE = Feature(final_sentence, None, 0.0)


class SentencingContentiousEnum(Enum):
    CUSTOMARY_PRACTICES = Feature(customary_practices, None, "Unknown")
    GENDER_STEREOTYPES = Feature(gender_stereotypes, None, "Unknown")
    OTHER_FACTORS = Feature(other_factors, None, "Unknown")
    IS_SOLE_BREADWINNER = Feature(is_sole_breadwinner, ["Yes", "No"], "No")
    GENDER_DISCRIMINATION_TYPE = Feature(gender_discrimination_type, None, "Unknown")
    SENTENCE_REDUCTION1 = Feature(sentence_reduction1, None, 0.0)
    SENTENCE_REDUCTION2 = Feature(sentence_reduction2, None, 0.0)


class SentencingSuspensionsEnum(Enum):
    LIFE_DEATH_PENALTY = Feature(life_death_penalty, ["Life", "Death", "NA"], "NA")
    SENTENCE_SUSPENDED = Feature(sentence_suspended, ["fully", "partially", "No"], "No")
    PRISON_SENTENCE = Feature(prison_sentence, ["Yes", "No", "Unknown"], "Unknown")
    CUMULATIVE_CONCURRENT_SENTENCE = Feature(cumulative_concurrent_sentence, ["cumulative", "concurrent", "Unknown"], "Unknown")
    OTHER_FORM_PUNISHMENT = Feature(other_form_punishment, None, "None")
    FINE_BOND = Feature(fine_bond, ["Yes", "No", "Unknown"], "Unknown")
    FINAL_SENTENCE_INCLUDING_SUSPENSION = Feature(final_sentence_including_suspension, None, 0.0)
    POSITIVE_JUDICIAL_STATEMENTS = Feature(positive_judicial_statements, None, "Unknown")
    NEGATIVE_JUDICIAL_STATEMENTS = Feature(negative_judicial_statements, None, "Unknown")
    NOTES = Feature(notes, None, "Unknown")   # MISSING


# In[34]:


FEATURE_GROUP_MAPPING = {
    doc_id: BasicFeatureEnum.DOC_ID,
    paclii_id: BasicFeatureEnum.PACLII_ID,
    is_victim_female: BasicFeatureEnum.IS_VICTIM_FEMALE,
    is_sentencing_decision: BasicFeatureEnum.IS_SENTENCING_DECISION,
    is_post_2000: BasicFeatureEnum.IS_POST_2000,
    is_applicable_case: BasicFeatureEnum.IS_APPLICABLE_CASE,
    case_type: CaseInfoEnum.CASE_TYPE,
    date: CaseInfoEnum.DATE,
    country: CaseInfoEnum.COUNTRY,
    city_district_of_hearing: CaseInfoEnum.COUNTRY,
    is_appellate_case: CaseInfoEnum.IS_APPELLATE_CASE,
    case_citation: CaseInfoEnum.CASE_CITATION,
    judicial_officer_name: CaseInfoEnum.JUDICIAL_OFFICER_NAME,
    courts_jurisdiction: CaseInfoEnum.COURTS_JURISDICTION,
    charges: CaseInfoEnum.CHARGES,
    charge_category: CaseInfoEnum.CHARGE_CATEGORY,
    is_anonymity_maintained: CaseInfoEnum.IS_ANONYMITY_MAINTAINED,
    victim_gender: VictimInfoEnum.VICTIM_GENDER,
    victim_age_at_offense: VictimInfoEnum.VICTIM_AGE_AT_OFFENSE,
    victim_is_adult_at_offense: VictimInfoEnum.VICTIM_IS_ADULT_AT_OFFENSE,
    victim_identify_as: VictimInfoEnum.VICTIM_IDENTIFY_AS,
    victim_disability: VictimInfoEnum.VICTIM_DISABILITY,
    perpetrator_gender: PerpetratorInfoEnum.PERPETRATOR_GENDER,
    perpetrator_age_at_offense: PerpetratorInfoEnum.PERPETRATOR_AGE_AT_OFFENSE,
    perpetrator_is_adult_at_offense: PerpetratorInfoEnum.PERPETRATOR_IS_ADULT_AT_OFFENSE,
    perpetrator_is_known_to_victim: PerpetratorInfoEnum.PERPETRATOR_IS_KNOWN_TO_VICTIM,
    perpetrator_relationship_with_victim: PerpetratorInfoEnum.PERPETRATOR_RELATIONSHIP_WITH_VICTIM,
    perpetrator_guilt: PerpetratorInfoEnum.PERPETRATOR_GUILT,
    perpetrator_first_time_offender_case: PerpetratorInfoEnum.PERPETRATOR_FIRST_TIME_OFFENDER_CASE,
    perpetrator_first_time_offender_self: PerpetratorInfoEnum.PERPETRATOR_FIRST_TIME_OFFENDER_SELF,
    pathology_report: AtHearingEnum.PATHOLOGY_REPORT,
    medical_report: AtHearingEnum.MEDICAL_REPORT,
    social_enquiry_report: AtHearingEnum.SOCIAL_ENQUIRY_REPORT,
    protection_order: SentencingBasicEnum.PROTECTION_ORDER,
    starting_sentence: SentencingBasicEnum.STARTING_SENTENCE,
    alternative_starting_sentence: SentencingBasicEnum.ALTERNATIVE_STARTING_SENTENCE,
    aggravating_factors: SentencingBasicEnum.AGGRAVATING_FACTORS,
    mitigating_factors: SentencingBasicEnum.MITIGATING_FACTORS,
    final_sentence: SentencingBasicEnum.FINAL_SENTENCE,
    customary_practices: SentencingContentiousEnum.CUSTOMARY_PRACTICES,
    gender_stereotypes: SentencingContentiousEnum.GENDER_STEREOTYPES,
    other_factors: SentencingContentiousEnum.OTHER_FACTORS,
    is_sole_breadwinner: SentencingContentiousEnum.IS_SOLE_BREADWINNER,
    gender_discrimination_type: SentencingContentiousEnum.GENDER_DISCRIMINATION_TYPE,
    sentence_reduction1: SentencingContentiousEnum.SENTENCE_REDUCTION1,
    sentence_reduction2: SentencingContentiousEnum.SENTENCE_REDUCTION2,
    life_death_penalty: SentencingSuspensionsEnum.LIFE_DEATH_PENALTY,
    sentence_suspended: SentencingSuspensionsEnum.SENTENCE_SUSPENDED,
    prison_sentence: SentencingSuspensionsEnum.PRISON_SENTENCE,
    cumulative_concurrent_sentence: SentencingSuspensionsEnum.CUMULATIVE_CONCURRENT_SENTENCE,
    other_form_punishment: SentencingSuspensionsEnum.OTHER_FORM_PUNISHMENT,
    fine_bond: SentencingSuspensionsEnum.FINE_BOND,
    final_sentence_including_suspension: SentencingSuspensionsEnum.FINAL_SENTENCE_INCLUDING_SUSPENSION,
    positive_judicial_statements: SentencingSuspensionsEnum.POSITIVE_JUDICIAL_STATEMENTS,
    negative_judicial_statements: SentencingSuspensionsEnum.NEGATIVE_JUDICIAL_STATEMENTS,
    notes: SentencingSuspensionsEnum.NOTES
}


# In[49]:


def list_features():
    fts = FEATURE_GROUP_MAPPING.keys()
    for feature in fts:
        possible_values = FEATURE_GROUP_MAPPING[feature].value.values
        default_value = FEATURE_GROUP_MAPPING[feature].value.default
        print(f"Feature: '{feature}'")
        print(f"Feature_Group: '{FEATURE_GROUP_MAPPING[feature].__class__.__name__}'")
        print(f"Possible_values: {possible_values}")
        print(f"Default_value: '{default_value}'")
        print()


# In[46]:


def validate_feature_value(feature_name, value, log_original=True) -> bool:
    if feature_name not in FEATURE_GROUP_MAPPING.keys():
        print(f"Incorrect feature '{feature_name}' provided.")
        return False
    possible_values = FEATURE_GROUP_MAPPING[feature_name].value.values
    default_value = FEATURE_GROUP_MAPPING[feature_name].value.default
    if log_original:
        print(f"Feature: '{feature_name}'")
        print(f"Possible values: {possible_values}")
        print(f"Default value: '{default_value}'")
    return value in possible_values if possible_values is not None else True


list_features()


# In[ ]:


# df with doc_id, feature_name, type, original_value, predicted_value, ignore, result

# FIXED VALUE FEATURES
# result df 1 feature name, accuracy
# result df 2 with feature group, avg accuracy

# NO FIXED VALUE FEATURES???


# In[ ]:




