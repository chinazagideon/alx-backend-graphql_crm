import datetime
import requests
import os

def log_crm_heartbeat():
    """
    Log a heartbeat to file and queries the GraphQL endpoint
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[$TIMESTAMP] CRM is alive\n"

    #append the hearbeat message to log file
    log_file_path = "/tmp/crm_heartbeat_log.txt"

    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message)

    #verify the GraphQL endpoint is reachable
    graphql_endpoint = "http://localhost:8000/graphql"
    query= "{ hello }"

    try: 
        response = requests.post(graphql_endpoint, json={'query': query})
        response.raise_for_status() #raise http error for bad requests
        print("GraphQL endpoint is reachable and healthy")
    except Exception as e:
        print(f"Error querying GraphQL endpoint failed: {e}")


