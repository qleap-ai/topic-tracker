import time
import json
from google.cloud import storage

import load_mwe_model
from tag_and_rank_articles import compute_tags_and_rank

all_clusters = {'frames': [], 'file_names': [], 'topics': load_mwe_model.topics}
topics = set()
storage_client = storage.Client()


def save(tagged_articles, file_name):
    tmp_file = "/Users/laemmel/svn/qleap/graph/topics/" + file_name
    with open(tmp_file, "w") as tmp:
        json.dump(tagged_articles, tmp)
    bucket_name = "qleap.ai"
    source_blob_name = "topics/" + file_name
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.upload_from_filename(tmp_file)


for coeff in range(0, 120):
    print("round ", coeff)
    period = 24
    offset = coeff * period * 3600
    to = time.time() - offset
    fr = to - period * 3600
    tagged_articles = compute_tags_and_rank(fr, to)

    all_clusters['frames'].append({"loaded": False})
    file_name = str(tagged_articles['from_ts']) + "-" + str(tagged_articles['to_ts']) + ".json"
    all_clusters['file_names'].append(file_name)
    save(tagged_articles, file_name)

    print("---------")



    save(all_clusters, "topics.json")

# tmp_file = "/Users/laemmel/svn/qleap/graph/topics/topics.json"
# with open(tmp_file, "w") as tmp:
#     json.dump(all_clusters, tmp)

# bucket_name = "qleap.ai"
# storage_client = storage.Client()
# source_blob_name = "topics/topics.json"
# bucket = storage_client.bucket(bucket_name)
# blob = bucket.blob(source_blob_name)
# blob.upload_from_filename(tmp_file)
