import json
from elasticsearch import Elasticsearch, helpers
from timeit import default_timer as timer
import urllib3
import logging
import configparser

# Suppress only the single InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
CONFIG_FILE = 'config.conf'

# Read configuration settings
def read_config(section, key):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config.get(section, key)

# Initialize Elasticsearch client
# Other Constants
ELASTICSEARCH_HOST = read_config('elasticsearch_cloud', 'host')
ELASTICSEARCH_USER = read_config('elasticsearch_cloud', 'user')
ELASTICSEARCH_PASSWORD = read_config('elasticsearch_cloud', 'password')

es = Elasticsearch(
    [ELASTICSEARCH_HOST],
    verify_certs=False,
    basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD))

# Load data from the file
with open('output_legacy_elastic-50-new.json', 'r') as file:
    documents = json.load(file)

# Loop through the list and remove the '_id' field
for doc in documents:
    # Delete the _id key
    del doc['_id']

    # Index document into Elasticsearch
    es.index(index=doc['_index'], document=doc['_source'])


# fixme: preflight check that legacy and cloud indexes are available

# fixme: test the count of old elastic's docs and new ones:
# GET /patdocument-50/_count