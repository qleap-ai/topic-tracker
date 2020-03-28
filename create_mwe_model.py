from google.cloud import storage
import json

seeds = {'Corona': ['corona', 'covid'], 'The Cure': ['vaccine'], 'Diamond Princes': ['diamond_princes'],
         'Olympic Games': ['olympic'],
         'Lockdown': ['lockdown']}


def enhance_w_unigrams(base_model):
    base_model['The Cure'].add('remdesivir')
    base_model['The Cure'].add('chloroquine')
    base_model['The Cure'].add('antiviral_drug')
    base_model['The Cure'].add('clinical_trials')
    base_model['The Cure'].add('gilead_sciences')



def load_mwes(filename):
    bucket_name = "semantic_features"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob_name = "mwes/" + filename
    blob = bucket.blob(blob_name)
    dest = "/tmp/" + filename
    blob.download_to_filename(dest)

    with open(dest, encoding='utf8') as json_file:
        mwes = json.load(json_file)
    return set(mwes['mwes'])


def build_model():
    mwes = load_mwes("cum_current.json")
    base_model = {}
    for k in seeds.keys():
        my_mwes = []
        for seed in seeds[k]:
            for mwe in mwes:
                if seed in mwe:
                    my_mwes.append(mwe)
        base_model[k] = set(my_mwes)
    enhance_w_unigrams(base_model)
    corona = base_model.pop('Corona')
    return base_model, corona
