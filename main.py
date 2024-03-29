import json

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import xmltodict

from models.appd_controller_credentials import AppDControllerCredentials

load_dotenv()

basic = HTTPBasicAuth('splunk', os.environ.get('SPLUNK_PASSWORD'))
appd_basic = HTTPBasicAuth('appd', os.environ.get('APPD_PASSWORD'))


def pull_node_names(url, headers, tier_name):
    application_name = os.environ.get('APPLICATION_NAME')
    nodes_response = requests.get(
        f"{url}/applications/{application_name}/tiers/{tier_name}/nodes", headers=headers)
    nodes_dict = xmltodict.parse(nodes_response.text)
    node_names = []
    for key, value in nodes_dict.items():
        if key == 'name':
            node_names.append(f"{value}")
    return node_names


def pull_hardware_metrics(url, headers, tier_name, duration_in_minutes):
    application_name = os.environ.get('APPLICATION_NAME')
    cpu_params = {'metric-path': f'Application Infrastructure Performance|{tier_name}|Hardware Resources|CPU|%Busy',
                  'time-range-type': 'BEFORE_NOW',
                  'duration-in-mins': f'{duration_in_minutes}'}
    cpu_data_response = requests.get(f"{url}/applications/{application_name}/metric-data", params=cpu_params,
                                     headers=headers)
    memory_params = {
        'metric-path': f'Application Infrastructure Performance|{tier_name}|Hardware Resources|Memory|Used %',
        'time-range-type': 'BEFORE_NOW',
        'duration-in-mins': f'{duration_in_minutes}'}
    memory_data_response = requests.get(f"{url}/applications/{application_name}/metric-data", params=memory_params,
                                        headers=headers)

    metric_data = {}
    metric_data['cpu-used'] = xmltodict.parse(cpu_data_response.text)['metric-datas']
    metric_data['memory-used'] = xmltodict.parse(memory_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_load(url, headers, tier_name, bt_name, duration_in_minutes):
    application_name = os.environ.get('APPLICATION_NAME')
    metric_data_response = requests.get(
        f"{url}/applications/{application_name}/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CCalls%20per%20Minute&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_performance(url, headers, tier_name, bt_name, duration_in_minutes):
    application_name = os.environ.get('APPLICATION_NAME')
    metric_data_response = requests.get(
        f"{url}/applications/{application_name}/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CAverage%20Response%20Time%20%28ms%29&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_business_transaction_errors(url, headers, tier_name, bt_name, duration_in_minutes):
    application_name = os.environ.get('APPLICATION_NAME')
    metric_data_response = requests.get(
        f"{url}/applications/{application_name}/metric-data?metric-path=Business%20Transaction%20Performance%7CBusiness%20Transactions%7C{tier_name}%7C{bt_name}%7CErrors%20per%20Minute&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
        headers=headers)

    metric_data = xmltodict.parse(metric_data_response.text)['metric-datas']
    return metric_data


def pull_app_nodes(url, headers, duration_in_minutes):
    application_name = os.environ.get('APPLICATION_NAME')
    app_nodes_xml = requests.get(f"{url}/applications/{application_name}/nodes", headers=headers)
    app_nodes_dict = xmltodict.parse(app_nodes_xml.text)['nodes']['node']
    for app_node in app_nodes_dict:
        app_node_cpu_response = requests.get(
            f"{url}/applications/Server%20&%20Infrastructure%20Monitoring/metric-data?metric-path=Application%20Infrastructure%20Performance%7CRoot%7CIndividual%20Nodes%7C{app_node['machineName']}%7CHardware%20Resources%7CCPU%7C%25Busy&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
            headers=headers)
        app_node_cpu_xml = xmltodict.parse(app_node_cpu_response.text)['metric-datas']
        app_node_memory_response = requests.get(
            f"{url}/applications/Server%20&%20Infrastructure%20Monitoring/metric-data?metric-path=Application%20Infrastructure%20Performance%7CRoot%7CIndividual%20Nodes%7C{app_node['machineName']}%7CHardware%20Resources%7CCPU%7C%25Busy&time-range-type=BEFORE_NOW&duration-in-mins={duration_in_minutes}",
            headers=headers)
        app_node_memory_xml = xmltodict.parse(app_node_memory_response.text)['metric-datas']
        app_node['cpu-busy'] = app_node_cpu_xml
        app_node['memory-used'] = app_node_memory_xml

    return app_nodes_dict


def send_app_nodes(app_nodes, destination_url):
    for node in app_nodes:
        node_dir = {}
        node_dir['node'] = node
        node_json = json.dumps(node_dir)
        requests.post(destination_url, json=node_json, auth=basic, verify=False)


def pull_all_databases(url):
    databases_xml = requests.get(f"{url}/databases/servers", auth=appd_basic)
    return databases_xml


def send_all_databases(databases_dict, destination_url):
    for database in databases_dict:
        database_dir = {}
        database_dir['database'] = database
        database_json = json.dumps(database_dir)
        requests.post(destination_url, json=database_json, auth=basic, verify=False)


def pull_bt_related_metrics(url, headers, duration_in_minutes):
    application_name = os.environ.get('APPLICATION_NAME')
    metric_data_response = requests.get(f"{url}/applications/{application_name}/business-transactions", headers=headers)

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
        transaction['nodes'] = pull_node_names(url=url, headers=headers, tier_name=transaction['tierName'])
        business_transaction = {'business-transaction': transaction}
        json_transaction = json.dumps(business_transaction)
        requests.post(str(os.environ.get('SPLUNK_URL')), json=json_transaction, auth=basic, verify=False)
    return metric_data


def pull_data_from_appd(duration_in_minutes):
    controller_credentials = AppDControllerCredentials(url=str(os.environ.get('CONTROLLER_URL')),
                                                       token=str(os.environ.get('BEARER_TOKEN')))
    url = controller_credentials.url + "/controller/rest"

    business_transactions_data = pull_bt_related_metrics(url, controller_credentials.headers, duration_in_minutes)

    # Send all Nodes
    nodes_dict = pull_app_nodes(url=url, headers=controller_credentials.headers,
                                duration_in_minutes=duration_in_minutes)
    send_app_nodes(app_nodes=nodes_dict, destination_url=str(os.environ.get('SPLUNK_URL')))

    # Send all Databases
    databases_dict = pull_all_databases(url=url)
    send_all_databases(databases_dict=databases_dict, destination_url=str(os.environ.get('SPLUNK_URL')))

    return business_transactions_data


if __name__ == '__main__':
    response_json = pull_data_from_appd(duration_in_minutes=1440)
