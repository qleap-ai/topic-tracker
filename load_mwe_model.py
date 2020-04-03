import csv

seeds = {'Corona': ['corona', 'covid'], 'The Cure': ['vaccine'], 'Diamond Princes': ['diamond_princes'],
         'Olympic Games': ['olympic'],
         'Lockdown': ['lockdown']}

topics = ['Corona', 'Diamond Princess', 'Lockdown', 'The Cure', 'Olympic Games']


def enhance_model(base_model):
    base_model['The Cure']['remdesivir'] = 1.0
    base_model['The Cure']['chloroquine'] = 1.0
    base_model['The Cure']['antiviral_drug'] = 1.0
    base_model['The Cure']['clinical_trials'] = 1.0
    base_model['The Cure']['gilead_sciences'] = 1.0
    base_model['The Cure']['gilead'] = 1.0
    base_model['The Cure']['kaletra'] = 1.0
    base_model['The Cure']['foipan'] = 1.0
    base_model['The Cure']['avigan'] = 1.0
    base_model['Corona']['coronavirus'] = 1.0
    base_model['Corona']['covid_19'] = 1.0
    base_model['Lockdown']['lockdown'] = 1.0
    base_model['Lockdown']['shelter_in_place'] = 1.0
    base_model['Lockdown']['curb_movements'] = 1.0
    base_model['Lockdown']['social_distancing'] = 1.0
    base_model['Lockdown']['quarantine'] = 1.0


def load():
    ret = {}
    with open('model/corona_mwes.json', newline='\n') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(row['category'], row['feature'], row['normalized_chi2'])
            k = row['category']
            if k in ret.keys():
                ret[k][row['feature']] = float(row['normalized_chi2'])
            else:
                ret[k] = {row['feature']: float(row['normalized_chi2'])}
    enhance_model(ret)
    return ret
