"""
This script creates a new AppD Analytics Custom Sschema.
Details of the API call can be found in the official AppD documentation.
https://docs.appdynamics.com/appd/23.x/latest/en/extend-appdynamics/appdynamics-apis/analytics-events-api#id-.AnalyticsEventsAPIv23.1-create_schemaCreateEventSchema
"""
import json
import requests

GLOBAL_ACCOUNT_NAME = ""  # AppD Global Account Name - required for Analytics API
API_KEY = ""  # AppD API Key - requires permissions to publish events to the chosen schema
EVENT_SERVICE_ENDPOINT = ""  # e.g. https://fra-ana-api.saas.appdynamics.com
SCHEMA_NAME = ""  # name of the schema, e.g. defaultBaselines


def create_schema():
    """
    This function creates a schema for a new Analytics data source.
    :return: null
    """
    api_url = f"{EVENT_SERVICE_ENDPOINT}/events/schema/{SCHEMA_NAME}"
    request_headers = {
        "X-Events-API-AccountName": f"{GLOBAL_ACCOUNT_NAME}",
        "X-Events-API-Key": f"{API_KEY}",
        "Accept": "application/vnd.appd.events+json;v=2",
        "Content-Type": "application/vnd.appd.events+json;v=2"
    }

    # request_payload is the representation of a custom schema - this must be edited
    request_payload = {
        "schema":
            {
                "applicationId": "integer",
                "applicationName": "string",
                "defaultBaseline": "string"
            }
    }
    request = requests.post(url=api_url, headers=request_headers, data=json.dumps(request_payload))
    return print(request)


create_schema()
