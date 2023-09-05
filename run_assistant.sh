#!/bin/bash

#indexes=('patdocument-50' 'patdocument-3302')
indexes=('patdocument-50')

# Read the config.conf file and populate variables
read_config() {
    local section="$1"
    local key="$2"
    local value=$(grep -E "^\[$section\]" -A 9999 config.conf | grep -E "^\[$section\]|^\s*$key\s*=" | grep -A 1 "^\s*$key\s*=" | tail -n 1 | cut -d'=' -f2- | tr -d '[:space:]')
    echo "$value"
}

# Read Elasticsearch Legacy configuration
ELASTICSEARCH_LEGACY_HOST=$(read_config "elasticsearch_legacy" "elasticsearch_legacy_host")
ELASTICSEARCH_LEGACY_PORT=$(read_config "elasticsearch_legacy" "elasticsearch_legacy_port")
ELASTICSEARCH_LEGACY_PROTOCOL=$(read_config "elasticsearch_legacy" "elasticsearch_legacy_protocol")

# Read Elasticsearch Cloud configuration
ELASTICSEARCH_CLOUD_HOST=$(read_config "elasticsearch_cloud" "elasticsearch_cloud_host")
ELASTICSEARCH_CLOUD_PORT=$(read_config "elasticsearch_cloud" "elasticsearch_cloud_port")
ELASTICSEARCH_CLOUD_PROTOCOL=$(read_config "elasticsearch_cloud" "elasticsearch_cloud_protocol")
ELASTICSEARCH_CLOUD_USER=$(read_config "elasticsearch_cloud" "elasticsearch_cloud_user")
ELASTICSEARCH_CLOUD_PASSWORD=$(read_config "elasticsearch_cloud" "elasticsearch_cloud_password")

# Function to check if an endpoint exists
check_endpoint() {
    local protocol="$1"
    local host="$2"
    local port="$3"
    local user="$4"
    local password="$5"
    local response=$(curl -s -o /dev/null -w "%{http_code}" -u "$user:$password" "$protocol://$host:$port/")
    if [ "$response" -eq 200 ]; then
        echo "Endpoint $endpoint exists."
    else
        echo "Endpoint $endpoint does not exist or is unreachable."
    fi
}

# Check if Elasticsearch endpoints exist
check_endpoint "$ELASTICSEARCH_LEGACY_PROTOCOL" "$ELASTICSEARCH_LEGACY_HOST" "$ELASTICSEARCH_LEGACY_PORT" "fake" "fake"
check_endpoint "$ELASTICSEARCH_CLOUD_PROTOCOL" "$ELASTICSEARCH_CLOUD_HOST" "$ELASTICSEARCH_CLOUD_PORT" "$ELASTICSEARCH_CLOUD_USER" "$ELASTICSEARCH_CLOUD_PASSWORD"

# Function to check if a command is available
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install jq if not available
if ! command_exists jq; then
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "jq is not installed. Installing via brew..."
        brew install jq
    elif [[ "$(grep '^ID=' /etc/os-release)" == "ID=ubuntu" ]]; then
        echo "jq is not installed. Installing via apt-get..."
        sudo apt-get -y install jq  # For Ubuntu/Debian
    else
        echo "jq is not installed, and OS is not macOS or Ubuntu."
        exit 1
    fi
else
    echo "jq is already installed."
fi

for index in "${indexes[@]}"; do
    # Step 1 - Confirm the deletion
    echo -n "Do you want to delete the index $index in Elastic Cloud (needed only if already exists to re-run)? [y/N]: "
    read answer
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    if [ "$answer" == "y" ]; then
        curl -X DELETE "$ELASTICSEARCH_CLOUD_PROTOCOL://$ELASTICSEARCH_CLOUD_HOST:$ELASTICSEARCH_CLOUD_PORT/$index" -u "$ELASTICSEARCH_CLOUD_USER:$ELASTICSEARCH_CLOUD_PASSWORD"
        echo "Index $index has been deleted."
    fi

    # Step 2: Remove elasticsearch library
    pip3 uninstall -y elasticsearch

    # Step 3: Install elasticsearch=7.13.4 library with pip3
    pip3 install elasticsearch==7.13.4

    # Rest of your script for index migration and operations
    current_time=$(date "+%Y.%m.%d-%H.%M.%S")
    file_name="$index_${current_time}.json"

    python3 read_from_elastic_legacy.py "$index" "$ELASTICSEARCH_LEGACY_HOST" "$ELASTICSEARCH_LEGACY_PORT" > "$file_name"

    # Step 5: Remove elasticsearch library
    pip3 uninstall -y elasticsearch

    # Step 6: Install elasticsearch=8.8.0 library with pip3
    pip3 install elasticsearch==8.8.0

    python3 write_to_elastic_cloud.py "$index" "$ELASTICSEARCH_CLOUD_PROTOCOL" "$ELASTICSEARCH_CLOUD_HOST" "$ELASTICSEARCH_CLOUD_PORT" "$ELASTICSEARCH_CLOUD_USER" "$ELASTICSEARCH_CLOUD_PASSWORD" "$file_name"

    # Step 7: Compare document counts
    count_index_legacy=$(curl -s "$ELASTICSEARCH_LEGACY_PROTOCOL://$ELASTICSEARCH_LEGACY_HOST:$ELASTICSEARCH_LEGACY_PORT/$index/_count" | jq -r '.count')
    count_index_cloud=$(curl -s "$ELASTICSEARCH_CLOUD_PROTOCOL://$ELASTICSEARCH_CLOUD_HOST:$ELASTICSEARCH_CLOUD_PORT/$index/_count" -u "$ELASTICSEARCH_CLOUD_USER:$ELASTICSEARCH_CLOUD_PASSWORD" | jq -r '.count')

    if [ "$count_index_legacy" -eq "$count_index_cloud" ]; then
        echo "Successful: Both indices have the same document count: $count_index_cloud."
    else
        echo "Error: Document counts do not match. index_legacy: $count_index_legacy, index_cloud: $count_index_cloud."
    fi

    # Step 8 - Delete file
    echo -n "Do you want to delete $file_name file? [y/N]: "
    read answer
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    if [ "$answer" == "y" ]; then
        rm "$file_name"
    fi
    echo "Index $index migrated."
done