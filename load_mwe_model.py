import csv

seeds = {'Corona': ['corona', 'covid'], 'The Cure': ['vaccine'], 'Diamond Princes': ['diamond_princes'],
         'Olympic Games': ['olympic'],
         'Lockdown': ['lockdown']}


def enhance_model(base_model):
    base_model['The Cure']['remdesivir'] = 1.0
    base_model['The Cure']['chloroquine'] = 1.0
    base_model['The Cure']['antiviral_drug'] = 1.0
    base_model['The Cure']['clinical_trials'] = 1.0
    base_model['The Cure']['gilead_sciences'] = 1.0


def load():
    ret = {}
    with open('/Users/laemmel/tmp/news_mwes/Topics_Client_Corona_2020-M_c3__a4_r-31.csv', newline='\n') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(row['category'], row['feature'], row['normalized_chi2'])
            k = row['category']
            if k in ret.keys():
                ret[k][row['feature']] = float(row['normalized_chi2'])
            else:
                ret[k] = {row['feature']: float(row['normalized_chi2'])}
    enhance_model(ret)
    corona = ret.pop('Corona')
    return ret,corona


