import time
import json
from google.cloud import storage

import topic_clusterer

all_clusters = {'episodes': []}
topics = set()
for coeff in range(0, 100):
    print("round ", coeff)
    period = 24
    offset = coeff * period * 3600
    to = time.time() - offset
    fr = to - period * 3600

    topic_clusters = topic_clusterer.compute_topic_clusters(fr, to)
    for t in topic_clusters['topics'].keys():
        topics.add(t)
    # print(topic_clusters)
    all_clusters['episodes'].append(topic_clusters)
    print("---------")

all_clusters['topics'] = list(topics)

tmp_file = "/tmp/rank.json"
with open(tmp_file, "w") as tmp:
    json.dump(all_clusters, tmp)

bucket_name = "qleap.ai"
storage_client = storage.Client()
source_blob_name = "topics/topics.json"
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(source_blob_name)
blob.upload_from_filename(tmp_file)