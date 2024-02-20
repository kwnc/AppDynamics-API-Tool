import json

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import xmltodict
import shutil


from models.appd_controller_credentials import AppDControllerCredentials

load_dotenv()


def pull_hardware_resources(url, headers, tier_name, duration_in_minutes):
    params = {'metric-path': f'Application Infrastructure Performance|{tier_name}|Hardware Resources|CPU|%Busy',
              'time-range-type': 'BEFORE_NOW',
              'duration-in-mins': f'{duration_in_minutes}'}
    metric_data_response = requests.get(f"{url}/metric-data", params=params, headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_performance(url, headers, tier_name, bt_name, duration_in_minutes):
    metric_data_response = requests.get(
        f"{url}/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_business_transactions(url, headers, duration_in_minutes):
    metric_data_response = requests.get(
        f"{url}/business-transactions", headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['business-transactions']
    for transaction in metric_data['business-transaction']:
        transaction_name = transaction['name'].replace(r'/', '%2F')
        transaction['metric-data'] = pull_business_transaction_performance(url=url, headers=headers,
                                                                           tier_name=transaction['tierName'],
                                                                           bt_name=transaction_name,
                                                                           duration_in_minutes=duration_in_minutes)
        transaction['hardware-data'] = pull_hardware_resources(url=url, headers=headers,
                                                               tier_name=transaction['tierName'],
                                                               duration_in_minutes=duration_in_minutes)

    return metric_data


def pull_data_from_appd(duration_in_minutes):
    controller_credentials = AppDControllerCredentials(url=str(os.environ.get('CONTROLLER_URL')),
                                                       token=str(os.environ.get('BEARER_TOKEN')))
    url = controller_credentials.url + "/controller/rest/applications/GECO_PRO_FMO"

    business_transactions_data = pull_business_transactions(url, controller_credentials.headers, duration_in_minutes)

    return business_transactions_data


if __name__ == '__main__':
    response_json = pull_data_from_appd(duration_in_minutes=1440)
    print(response_json)

    with open("/home/ubuntu/AppDynamics-API-Tool/file.txt", "w") as f:
        f.write(str(response_json))

    basic = HTTPBasicAuth('splunk', os.environ.get('SPLUNK_PASSWORD'))

    response = requests.post('https://prd-p-kz2dg.splunkcloud.com:8088/services/collector/raw', json=response_json, auth=basic, verify=False)
    print(response.text)
