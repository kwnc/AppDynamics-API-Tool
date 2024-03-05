import json

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import xmltodict

from models.appd_controller_credentials import AppDControllerCredentials

load_dotenv()

basic = HTTPBasicAuth('splunk', os.environ.get('SPLUNK_PASSWORD'))


def pull_hardware_metrics(url, headers, tier_name, duration_in_minutes):
    cpu_params = {'metric-path': f'Application Infrastructure Performance|{tier_name}|Hardware Resources|CPU|%Busy', 'time-range-type': 'BEFORE_NOW',
              'duration-in-mins': f'{duration_in_minutes}'}
    cpu_data_response = requests.get(f"{url}/applications/GECO_PRO_FMO/metric-data", params=cpu_params, headers=headers)
    memory_params = {'metric-path': f'Application Infrastructure Performance|{tier_name}|Hardware Resources|Memory|Used %', 'time-range-type': 'BEFORE_NOW',
              'duration-in-mins': f'{duration_in_minutes}'}
    memory_data_response = requests.get(f"{url}/applications/GECO_PRO_FMO/metric-data", params=memory_params, headers=headers)

    metric_data = {}
    metric_data['cpu-used'] = xmltodict.parse(cpu_data_response.text)['metric-datas']
    metric_data['memory-used'] = xmltodict.parse(memory_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_load(url, headers, tier_name, bt_name, duration_in_minutes):
    metric_data_response = requests.get(
        f"{url}/applications/GECO_PRO_FMO/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CCalls%20per%20Minute&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_performance(url, headers, tier_name, bt_name, duration_in_minutes):
    metric_data_response = requests.get(
        f"{url}/applications/GECO_PRO_FMO/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_errors(url, headers, tier_name, bt_name, duration_in_minutes):
    metric_data_response = requests.get(
        f"{url}/applications/GECO_PRO_FMO/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CErrors%20per%20Minute&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_nodes_information(url, headers, tier_name):
    tier_nodes_xml = requests.get(f"{url}/applications/GECO_PRO_FMO/tiers/{tier_name}/nodes", headers=headers)
    tier_nodes_dict = xmltodict.parse(tier_nodes_xml.text)['nodes']
    return tier_nodes_dict


def pull_databases(url, headers):
    databases_xml = requests.get(f"{url}/databases/servers", headers=headers)
    return databases_xml.text


def pull_bt_related_metrics(url, headers, duration_in_minutes):
    metric_data_response = requests.get(f"{url}/applications/GECO_PRO_FMO/business-transactions", headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['business-transactions']
    for transaction in metric_data['business-transaction']:
        transaction_name = transaction['name'].replace(r'/', '%2F')
        transaction['load'] = pull_business_transaction_load(url=url, headers=headers,
                                                                           tier_name=transaction['tierName'],
                                                                           bt_name=transaction_name,
                                                                           duration_in_minutes=duration_in_minutes)
        transaction['average-response-time'] = pull_business_transaction_performance(url=url, headers=headers,
                                                                           tier_name=transaction['tierName'],
                                                                           bt_name=transaction_name,
                                                                           duration_in_minutes=duration_in_minutes)
        transaction['errors-per-minute'] = pull_business_transaction_errors(url=url, headers=headers,
                                                                           tier_name=transaction['tierName'],
                                                                           bt_name=transaction_name,
                                                                           duration_in_minutes=duration_in_minutes)
        transaction['hardware-data'] = pull_hardware_metrics(url=url, headers=headers,
                                                               tier_name=transaction['tierName'],
                                                               duration_in_minutes=duration_in_minutes)
        transaction['nodes'] = pull_nodes_information(url=url, headers=headers, tier_name=transaction['tierName'])
        transaction['databases'] = pull_databases(url=url, headers=headers)
        json_transaction = json.dumps(transaction)
        with open("/home/ubuntu/AppDynamics-API-Tool/file.json", "w") as f:
            f.write(json_transaction)
        requests.post('https://prd-p-nfjje.splunkcloud.com:8088/services/collector/raw', json=json_transaction, auth=basic, verify=False)

    return metric_data


def pull_data_from_appd(duration_in_minutes):
    controller_credentials = AppDControllerCredentials(url=str(os.environ.get('CONTROLLER_URL')),
                                                       token=str(os.environ.get('BEARER_TOKEN')))
    url = controller_credentials.url + "/controller/rest"

    business_transactions_data = pull_bt_related_metrics(url, controller_credentials.headers, duration_in_minutes)

    return business_transactions_data


if __name__ == '__main__':
    response_json = pull_data_from_appd(duration_in_minutes=1440)
    print(response_json)
