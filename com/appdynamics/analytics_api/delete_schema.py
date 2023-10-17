"""
This script creates a new AppD Analytics Custom Sschema.
Details of the API call can be found in the official AppD documentation.
https://docs.appdynamics.com/appd/23.x/latest/en/extend-appdynamics/appdynamics-apis/analytics-events-api#id-.AnalyticsEventsAPIv23.1-delete_schemaDeleteEventSchema
"""
import json
import requests

GLOBAL_ACCOUNT_NAME = ""  # AppD Global Account Name - required for Analytics API
API_KEY = ""  # AppD API Key - requires permissions to publish events to the chosen schema
EVENT_SERVICE_ENDPOINT = ""  # e.g. https://fra-ana-api.saas.appdynamics.com
SCHEMA_NAME = ""  # name of the schema, e.g. defaultBaselines


def delete_schema():
    """
    This function removes a schema from AppD Analytics data source.
    :return: null
    """
    api_url = f"{EVENT_SERVICE_ENDPOINT}/events/schema/{SCHEMA_NAME}"
    request_headers = {
        "X-Events-API-AccountName": f"{GLOBAL_ACCOUNT_NAME}",
        "X-Events-API-Key": f"{API_KEY}"
    }
    request = requests.delete(url=api_url, headers=request_headers)
    return print(request)


delete_schema()
