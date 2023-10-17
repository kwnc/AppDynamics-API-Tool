import requests
import logging


def get_access_token(url, account, api_client, secret):
    api_url = f"{url}/controller/api/oauth/access_token"
    request_payload = f"grant_type=client_credentials&client_id={api_client}@{account}&client_secret={secret}"
    request_header = {"Content-Type": "application/x-www-form-urlencoded"}
    request_token = requests.post(api_url, data=request_payload, headers=request_header)
    request_response = request_token.json()
    logging.info(f"Access token generated: {str(request_response['access_token'])[:5]} ***")
    return request_response['access_token']
