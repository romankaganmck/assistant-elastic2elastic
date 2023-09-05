import json
import sys
from elasticsearch import Elasticsearch
import urllib3
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


ELASTICSEARCH_INDEX = sys.argv[1]
ELASTICSEARCH_CLOUD_PROTOCOL = sys.argv[2]
ELASTICSEARCH_CLOUD_HOST = sys.argv[3]
ELASTICSEARCH_CLOUD_PORT = sys.argv[4]
ELASTICSEARCH_CLOUD_USER = sys.argv[5]
ELASTICSEARCH_CLOUD_PASSWORD = sys.argv[6]
FILE_NAME = sys.argv[7]
# Initialize Elasticsearch client
es = Elasticsearch(
    [ELASTICSEARCH_CLOUD_PROTOCOL+"://"+ELASTICSEARCH_CLOUD_HOST+":"+ELASTICSEARCH_CLOUD_PORT+"/"],
    verify_certs=False,
    basic_auth=(ELASTICSEARCH_CLOUD_USER, ELASTICSEARCH_CLOUD_PASSWORD))

# Define the mapping in a function
def create_index_with_mapping(index_name):
    settings = {
        "number_of_shards": 2,
        "number_of_replicas": 2
    }

    mapping = {
        "properties": {
            "Deleted": {"type": "boolean"},
            "Text": {
                "type": "keyword",
                "ignore_above": 2560  # Apply ignore_above setting
            },
            "DocumentName": {"type": "text"},
            "Draft": {"type": "boolean"},
            "PracticeId": {"type": "long"},
            "OwnerUserId": {"type": "long"},
            "AuthorName": {"type": "text"},
            "CreatedDate": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss.SSS"
            },
            "Id": {"type": "integer"},
            "PatientId": {"type": "long"},
            "Sections": {"type": "text"},  # Adjust type as needed
            "DateOfService": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss.SSS"
            }
        }
    }

    # Create the index with the custom mapping
    es.indices.create(index=index_name, mappings=mapping, settings=settings)


    if es.indices.exists(index=index_name) == False:
        # Create index with mapping
        create_index_with_mapping(ELASTICSEARCH_INDEX)

# Load data from the file
with open(FILE_NAME, 'r') as file:
    documents = json.load(file)

# Loop through the list and remove the '_id' field
for doc in documents:
    # Index document into Elasticsearch
    es.index(index=ELASTICSEARCH_INDEX, document=doc['_source'])
