"""
This script publishes default baselines chosen for all Controller's applications.
"""
import logging
import requests
from com.appdynamics.utils import get_access_token

BASE_URL = "https://<account>>.saas.appdynamics.com"  # Controller URL
ACCOUNT = ""  # Account name
API_CLIENT_NAME = ""  # API Client Name
SECRET = ""  # API Client's Secret
GLOBAL_ACCOUNT_NAME = ""  # AppD Global Account Name - required for Analytics API
API_KEY = ""  # AppD API Key - requires permissions to publish events to the chosen schema
EVENT_SERVICE_ENDPOINT = ""  # e.g. https://fra-ana-api.saas.appdynamics.com
ACCESS_TOKEN = get_access_token(url=BASE_URL, api_client=API_CLIENT_NAME, account=ACCOUNT, secret=SECRET)


def get_default_baseline(application_id):
    """
    Method is based on an unsupported, UI endpoint that returns application's default baseline.
    :param application_id: AppD app id
    :return: chosen default baseline
    """
    api_url = f"{BASE_URL}/controller/restui/baselines/getDefaultBaseline/{str(application_id)}"
    request_headers = {f"authorization": "Bearer {ACCESS_TOKEN}"}
    request_response = requests.get(api_url, headers=request_headers)
    response_json = request_response.json()
    return response_json['name']


def get_all_applications():
    api_url = BASE_URL + "/controller/rest/applications"
    request_headers = {f"authorization": "Bearer {ACCESS_TOKEN}"}
    request_response = requests.get(api_url, headers=request_headers, params="output=JSON")
    return request_response.json()


def create_event():
    """
    This method publishes AppD Analytics Events containing application and its chosen default baseline.
    :return: null
    """
    api_url = f"{EVENT_SERVICE_ENDPOINT}/events/publish/defaultBaselines"  # For Frankfurt SaaS region
    request_headers = {
        "X-Events-API-AccountName": f"{GLOBAL_ACCOUNT_NAME}",
        "X-Events-API-Key": f"{API_KEY}",
        "Content-Type": "application/vnd.appd.events+json;v=2",
    }

    applications = get_all_applications()

    for i in applications:
        baseline = get_default_baseline(i['id'])
        app_id = i['id']
        app_name = i['name']
        logging.info(f"The default baseline for the application {app_name} (id: {app_id}) is {baseline}")

        request_payload = [
            {
                "applicationId": app_id,
                "applicationName": app_name,
                "defaultBaseline": baseline
            }
        ]

        # publish event
        response = requests.post(url=api_url, headers=request_headers, json=request_payload)

        # validate the request
        if response.status_code == 200:
            logging.info("Default Baselines published. Status code " + str(response.status_code))
        elif response.status_code == 400:
            logging.error(f"The given request was invalid. {response}")
        elif response.status_code == 401:
            logging.error(
                f"The given authentication information provided in the authorization header was invalid. {response}")
        elif response.status_code == 404:
            logging.error(f"No event type could be found for this account. {response}")
        elif response.status_code == 406:
            logging.error(f"The Accept header was not application/vnd.appd.events+json;v=2. {response}")
        elif response.status_code == 413:
            logging.error(f"The request body is larger than the max allowed size. {response}")
        elif response.status_code == 415:
            logging.error(f"The Content-Type header was not application/vnd.appd.events+json;v=2. {response}")
        elif response.status_code == 429:
            logging.error(f"Too many requests. Returned when account or event reaches limits. {response}")
        else:
            logging.error(f"Default Baselines not published - unknown error. {response}")


if __name__ == '__main__':
    create_event()
