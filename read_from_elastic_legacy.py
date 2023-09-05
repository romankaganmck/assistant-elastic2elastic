# coding:utf-8
from elasticsearch import Elasticsearch
import json
import sys


# Initialize Elasticsearch client
# Other Constants
ELASTICSEARCH_INDEX = sys.argv[1]
ELASTICSEARCH_LEGACY_HOST = sys.argv[2]
ELASTICSEARCH_LEGACY_PORT = sys.argv[3]

timeout = 500
doc_type = None
batch_size = 5000
body = {
    "query": {
        "match_all": {}
    }
}

# Init Elasticsearch instance
try:
    es = Elasticsearch(
        [{'host': ELASTICSEARCH_LEGACY_HOST, 'port': ELASTICSEARCH_LEGACY_PORT}],
        timeout=5000
    )
except Exception as e:
    print(f"Error while searching: {e}")
    sys.exit(1)


# Initialize a flag for printing the first item
first_item = True


# Process hits here
def process_hits(hits):
    global first_item
    for item in hits:
        # Remove unnecessary fields
        item.pop('_index', None)
        item.pop('_type', None)
        item.pop('_id', None)
        item.pop('_score', None)
        if not first_item:
            print(",")  # Add a comma separator between items
        else:
            first_item = False
        # Print the modified item
        print(json.dumps(item, ensure_ascii=False, indent=3).replace('\u00A0', ' '))


# Check index exists
if not es.indices.exists(index=ELASTICSEARCH_INDEX):
    print("Index " + ELASTICSEARCH_INDEX + " not exists")
    sys.exit(5154)

# Init scroll by search
data = es.search(
    index=ELASTICSEARCH_INDEX,
    doc_type=doc_type,
    scroll='2m',
    size=batch_size,
    body=body
)

# Get the scroll ID
sid = data['_scroll_id']
scroll_size = len(data['hits']['hits'])

print("[")
while scroll_size > 0:
    # Before scroll, process current batch of hits
    process_hits(data['hits']['hits'])
    data = es.scroll(scroll_id=sid, scroll='2m')
    # Update the scroll ID
    sid = data['_scroll_id']
    # Get the number of results that returned in the last scroll
    scroll_size = len(data['hits']['hits'])
print("]")
