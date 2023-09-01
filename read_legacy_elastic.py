# coding:utf-8
from elasticsearch import Elasticsearch
import json

# Define config
host = "pd-g2-es-1.production.iknowmed.com"
port = 9200
timeout = 5000
index = "patdocument-50"
doc_type = None
size = 500
body = {
    "query": {
        "match_all": {}  # Define your query here
    }
}

# Init Elasticsearch instance
es = Elasticsearch(
    [{'host': host, 'port': port}],
    timeout=timeout
)

# Initialize a flag for printing the first item
first_item = True

# Process hits here
def process_hits(hits):
    global first_item
    for item in hits:
        if not first_item:
            print(",")  # Add a comma separator between items
        else:
            first_item = False

        print(json.dumps(item, ensure_ascii=False, indent=3).replace('\u00A0', ' '))

# Check index exists
if not es.indices.exists(index=index):
    print("Index " + index + " not exists")
    exit()

# Init scroll by search
data = es.search(
    index=index,
    doc_type=doc_type,
    scroll='2m',
    size=size,
    body=body
)

# Get the scroll ID
sid = data['_scroll_id']
scroll_size = len(data['hits']['hits'])

print("[")
while scroll_size > 0:
    # print("Scrolling...")

    # Before scroll, process current batch of hits
    process_hits(data['hits']['hits'])

    data = es.scroll(scroll_id=sid, scroll='2m')

    # Update the scroll ID
    sid = data['_scroll_id']

    # Get the number of results that returned in the last scroll
    scroll_size = len(data['hits']['hits'])

print("]")