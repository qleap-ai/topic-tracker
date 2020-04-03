import json
from google.cloud import storage
import time

import collections

from tag_and_rank_articles import compute_tags_and_rank

storage_client = storage.Client()
bucket_name = "qleap.ai"


def save(tagged_articles, file_name):
    tmp_file = "/tmp/" + file_name
    with open(tmp_file, "w") as tmp:
        json.dump(tagged_articles, tmp)

    source_blob_name = "topics/" + file_name
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.upload_from_filename(tmp_file)


def load(name):
    tmp_file = "/tmp/" + name
    bucket = storage_client.bucket(bucket_name)
    blob_name = "topics/" + name
    blob = bucket.blob(blob_name)

    blob.download_to_filename(tmp_file)
    with open(tmp_file, encoding='utf8') as json_file:
        topics = json.load(json_file)
    return topics


def run(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    topics = load("topics.json")
    last_frame = load(topics['file_names'][0])

    fr = last_frame['to_ts']
    to = time.time()
    tagged_articles = compute_tags_and_rank(fr, to)
    file_name = str(tagged_articles['from_ts']) + "-" + str(tagged_articles['to_ts']) + ".json"
    file_names = collections.deque(topics['file_names'])
    file_names.pop()
    file_names.appendleft(file_name)
    save(tagged_articles, file_name)
    topics['file_names'] = list(file_names)
    save(topics, "topics.json")


run("","")