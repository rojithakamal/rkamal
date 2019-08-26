import json
import logging
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from iotfunctions import bif
from custom.functions import MaximoAssetHTTPPreload
from iotfunctions.metadata import EntityType
from iotfunctions.db import Database
#from iotfunctions.enginelog import EngineLogging
from custom import settings

#EngineLogging.configure_console_logging(logging.DEBUG)

'''
# Replace with a credentials dictionary or provide a credentials
# Explore > Usage > Watson IOT Platform Analytics > Copy to clipboard
# Past contents in a json file.
'''
#with open('credentials_staging.json', encoding='utf-8') as F:
with open('credentials.json', encoding='utf-8') as F:
#with open('credentials_dev.json', encoding='utf-8') as F:
    credentials = json.loads(F.read())

'''
Developing Test Pipelines
-------------------------
When creating a set of functions you can test how they these functions will
work together by creating a test pipeline.
'''


'''
Create a database object to access Watson IOT Platform Analytics DB.
'''
db = Database(credentials = credentials)
db_schema = None #  set if you are not using the default

'''
To do anything with IoT Platform Analytics, you will need one or more entity type.
You can create entity types through the IoT Platform or using the python API as shown below.
The database schema is only needed if you are not using the default schema. You can also rename the timestamp.
'''
entity_name = 'kalbuildings'
db_schema = "BLUADMIN" # None  # replace if you are not using the default schema
db.drop_table(entity_name, schema = db_schema)

# Credentials to access Building Insights API.
BI_USERNAME = settings.BI_USERNAME
BI_PASSWORD = settings.BI_PASSWORD
BI_TENANT_ID = settings.BI_TENANT_ID

print("BI_Credentials")
print(BI_USERNAME)
print(BI_PASSWORD)
print(BI_TENANT_ID)

entity = EntityType(entity_name, db,
                    # following columns can be dynamically generated based on meters associated with each asset
                    Column('building',String(50)),
                    Column('energy_value',Float()),
                    Column('energy_unit',String(50)),
                    Column('temperature',Float()),
                    Column('temperature_unit',String(50)),
                    # Column('energy_value',Float()),
                    # Column('energy_compare_percent', Float()),
                    # Column('energy_unit',String(50)),
                    # Column('energy_trend',String(50)),
                    # Column('energy_trend_status',String(50)),
                    MaximoAssetHTTPPreload( username = BI_USERNAME,
                                    password = BI_PASSWORD,
                                    request='GET',
                                    url=BI_TENANT_ID,
                                    output_item = 'http_preload_done'),
                    bif.PythonExpression(expression='df["energy_value"]*df["energy_value"]',
                                         output_name = 'volume'),
                    **{
                      '_timestamp' : 'evt_timestamp',
                      '_db_schema' : db_schema
})


'''
When creating an EntityType object you will need to specify the name of the entity, the database
object that will contain entity data

After creating an EntityType you will need to register it so that it visible in the Add Data to Entity Function UI.
To also register the functions and constants associated with the entity type, specify
'publish_kpis' = True.
'''
entity.register(raise_error=False)
db.register_functions([MaximoAssetHTTPPreload])

'''
To test the execution of kpi calculations defined for the entity type locally
use this function.

A local test will not update the server job log or write kpi data to the AS data
lake. Instead kpi data is written to the local filesystem in csv form.
'''

entity.exec_local_pipeline()

'''
view entity data
'''
# can get entity metadata with following
#
# TODO, for some reason this returns data but also throws exception.
'''
meta = db.get_entity_type(entity_name)
db_schema = meta['schemaName']
table_name = meta['metricTableName']
'''
db_schema = "BLUADMIN"
table_name = "kalbuildings"

df = db.read_table(table_name=table_name, schema=db_schema)
# df = db.read_table(table_name=entity_name, schema=db_schema)
print(df.head())


print ( 'Done registering  entity %s '  %db.register_functions([MaximoAssetHTTPPreload]) )
