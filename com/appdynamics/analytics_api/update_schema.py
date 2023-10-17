"""
This script creates a new AppD Analytics Custom Sschema.
Details of the API call can be found in the official AppD documentation.
https://docs.appdynamics.com/appd/23.x/latest/en/extend-appdynamics/appdynamics-apis/analytics-events-api#id-.AnalyticsEventsAPIv23.1-update_schemaUpdateEventSchema
"""
import json
import requests

GLOBAL_ACCOUNT_NAME = ""  # AppD Global Account Name - required for Analytics API
API_KEY = ""  # AppD API Key - requires permissions to publish events to the chosen schema
EVENT_SERVICE_ENDPOINT = ""  # e.g. https://fra-ana-api.saas.appdynamics.com
SCHEMA_NAME = ""  # name of the schema, e.g. defaultBaselines


def update_schema():
    """
    This function updates a schema from AppD Analytics data source.
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
        "add":
            {
                "newFiled": "integer"
            },
        "rename": {
            "applicationName": "appName"
        }
    }
    request = requests.patch(url=api_url, headers=request_headers, data=json.dumps(request_payload))
    return print(request)


update_schema()
