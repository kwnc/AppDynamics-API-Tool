# Get Default AppD Baseline
This scripts handle creating the custom, AppD schema, as well as publishing the events with default AppD [Baseline](https://docs.appdynamics.com/appd/23.x/latest/en/application-monitoring/business-transactions/monitor-the-performance-of-business-transactions/dynamic-baselines) chosen for all applications.
----
## Publishing Events
Once the schema has been created, the user can publish events by running the [publish_default_baselines.py](com%2Fappdynamics%2Fpublish_default_baselines.py) script. Details on publishing Custom analytics Events can be found in the official AppD documentation: [Create Event Schema](https://docs.appdynamics.com/appd/23.x/latest/en/extend-appdynamics/appdynamics-apis/analytics-events-api#id-.AnalyticsEventsAPIv23.1-create_schemaCreateEventSchema).

### Publishing Events Script
To publish an event (in this example all default baselines), edit global variables in the [publish_default_baselines.py](com%2Fappdynamics%2Fpublish_default_baselines.py) and run the script.
Variables to be edited:
- GLOBAL_ACCOUNT_NAME
  - The global account name, as shown in the Controller UI License page
- API_KEY
  - The Analytics API key. See [Manage API Keys](https://docs.appdynamics.com/appd/23.x/latest/en/analytics/deploy-analytics-with-the-analytics-agent/analytics-and-data-security/manage-api-keys)
- BASE_URL
  - e.g. "https://rdc.saas.appdynamics.com"
- ACCOUNT
  -  Account name e.g. "rdc" or "rdcdev" 
- API_CLIENT_NAME
  - [AppD API Client's](https://docs.appdynamics.com/appd/23.x/latest/en/extend-appdynamics/appdynamics-apis/api-clients) Name
- SECRET
  - API Client's Secret 
----
## Creating new schema

**This can be run ONLY ONCE**

The AppD Custom Analytics schema can be created by using AppD API: [Create AppD Event Schema](https://docs.appdynamics.com/appd/23.x/latest/en/extend-appdynamics/appdynamics-apis/analytics-events-api#id-.AnalyticsEventsAPIv23.1-create_schemaCreateEventSchema). To create a new schema using this script, edit global variables in the [create_schema.py](com%2Fappdynamics%2Fanalytics_api%2Fcreate_schema.py) file and run it. For the DEV Controller, schema has been created.

Variables to be edited:
- GLOBAL_ACCOUNT_NAME
  - The global account name, as shown in the Controller UI License page
- API_KEY
  - The Analytics API key. See [Manage API Keys](https://docs.appdynamics.com/appd/23.x/latest/en/analytics/deploy-analytics-with-the-analytics-agent/analytics-and-data-security/manage-api-keys)
  
You can create, delete and update the schema following the official AppD documentation. If you'd like to change the schema itself, edit the `request_payload` variable in the script's function.

----

As this is not official AppD Product's feature, this script is not supported by AppD Support. This is a workaround created by AppD PS engineer who willingly will help with requests.  
