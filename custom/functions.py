import inspect
import logging
import datetime as dt
import math
from sqlalchemy.sql.sqltypes import TIMESTAMP,VARCHAR
import numpy as np
import pandas as pd
import json
import base64
import requests

#from iotfunctions.base import BaseTransformer
from iotfunctions.base import BasePreload
from iotfunctions import ui
from iotfunctions.db import Database
from iotfunctions import bif
#import datetime as dt
import datetime
import urllib3
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


# Specify the URL to your package here.
# This URL must be accessible via pip install
#PACKAGE_URL = 'git+https://github.com/madendorff/functions@'
PACKAGE_URL = 'git+https://github.com/rojithakamal/rkamal'

class MaximoAssetHTTP(BasePreload):
    '''
    Do a HTTP request as a preload activity. Load results of the get into the Entity Type time series table.
    HTTP request is experimental
    '''

    out_table_name = None

    def __init__(self, username, password, request, url, headers = None, body = None, column_map = None, output_item  = 'http_preload_done'):

        if body is None:
            body = {}

        if headers is None:
            headers = {}

        if column_map is None:
            column_map = {}

        super().__init__(dummy_items=[],output_item = output_item)

        # create an instance variable with the IBM IOT Platform Analytics Service Function input arguments.

        self.username = username
        logging.debug('self.username %s' %self.username)
        self.url = url
        self.password = password
        logging.debug('self.password %s' %self.password)
        # self.tenant = url
        # logging.debug('tenantid self.tenant %s' %self.tenant)
        self.request = request
        logging.debug('self.request %s' %self.request)
        self.headers = headers
        logging.debug('headers %s' %headers)

        self.template_id = "building"
        # TODO, user needs to set this initially
        self.realm = True
        self.realm_token = None
        self.realm_user = "betauser"
        self.realm_pass = "betauser"

        self.body = body
        logging.debug('body %s' %body)
        self.column_map = column_map
        logging.debug('column_map %s' %column_map)

        # generate base64 auth
        self.token = base64.b64encode(bytes(username + ':'  + password, 'utf-8')).decode('ascii')
        if headers:
            self.headers['maxauth'] = self.token
        else:
            self.headers = {
                "maxauth": self.token
            }


    def getMeters (self, asset_id = None):
        # hardcoding id for test TODO
        # asset_id = "2112"
        q_endpoint = self.url + "/maximo/oslc/os/mxasset?oslc.select=assetmeter&oslc.where=assetnum=" + asset_id
        headers = { "maxauth": self.token }
        res = requests.get(q_endpoint, headers=headers, cookies=self.cookies)
        meters = []
        try:
            meters = res.json()["rdfs:member"][0]["spi:assetmeter"]
            print(str(len(meters)) + " meters found")
        except:
            print("no meters found")
            pass
        return meters
        # if (len(meters) > 0):
        #     meter_readings = []
        #     # trim payload down to last reading
        #     # TODO, possible to get all historical readings?
        #     for meter in meters:
        #         print(meter)
        #         try:
        #             meter_readings.append({
        #                 meter['spi:metername']: meter['spi:lastreading']
        #             })
        #         except:
        #             print("no meter data found for meter: " + meter['spi:metername'])
        #             pass
        #     print(meter_readings)
        #return # metrics_value, metrics_unit, metrics_compare_percent, metrics_trend, metrics_trend_status

        # return metrics_value, metrics_unit, metrics_compare_percent, metrics_trend, metrics_trend_status


        # '''
        # [
        # "buildingName":
        #     {
        #         "temp": "75",
        #         "energy": "15kw"
        #     }
        # ]
        # '''
        #
        # '''
        # # input list of buildings and Returns list of energy by building.
        #
        # # wastage: Provides energy wastage of this building for last 30 days. Provides % Wastage compared to total energy usage of that building. Wastage is calculated as the sum of excess energy consumed over the upper bound of the predicted energy, in the last 30 days.
        # {
        #   "value": 0,
        #   "unit": "string",
        #   "usage_percent": 0
        # }
        #
        # # usage: Provides energy consumption of this building for last 30 days. Provide % Up or Down compared to same 30 days of the last year
        # {
        #   "value": 0,
        #   "unit": "string",
        #   "compare_percent": 0,
        #   "trend": "string",
        #   "trend_status": "string"
        # }
        #
        # # prediction:  Returns the energy usage for last 48 hours, energy prediction for next 48 hours and the trend whether its up or down
        # {
        #   "value": 0,
        #   "unit": "string",
        #   "trend": "string",
        #   "trend_status": "string",
        #   "last_value": 0,
        #   "last_unit": "string"
        # }
        # '''
        #
        # '''
        # # Initialize building energy metrics to retrieve
        # '''
        # metrics_value = []
        # metrics_unit  = []
        # metrics_compare_percent  = []
        # metrics_trend = []
        # metrics_trend_status = []
        #
        # logging.debug("Getting Energy")
        # header = {}
        # # auth_str = 'Bearer '+ self.token
        # #header = { 'Authorization':  }
        # header['maxauth'] = self.token
        # body = {}
        # energy_data_options = ['usage']
        #
        #
        # for bldg in buildings:
        #     logging.debug("getMeters for buiding %s "  %bldg)
        #
        #     for etype in energy_data_options:
        #         logging.debug("getMeters type %s " %etype  )
        #         uri = "https://" + self.tenant + "-agg.mybluemix.net/api/v1/building/energy/" + etype
        #         logging.debug("uri %s" %uri)
        #         req = self.db.http.request('GET',
        #                          uri,
        #                          fields={'buildingName': bldg
        #                                  },
        #                          body=body,
        #                          headers= header)
        #         if req.status == 200:
        #             logging.debug("energy_metrics req.data  %s" %req.data )
        #             # '{"value":16.3,"unit":"MWh","compare_percent":7.34,"trend":"DOWN","trend_status":"GREEN"}'
        #             energy_metrics_json = json.loads(req.data.decode('utf-8'))
        #             metrics_value.append(energy_metrics_json['value'])
        #             metrics_unit.append(energy_metrics_json['unit'])
        #             metrics_compare_percent.append(energy_metrics_json['compare_percent'])
        #             metrics_trend.append(energy_metrics_json['trend'])
        #             metrics_trend_status.append(energy_metrics_json['trend_status'])
        #         else:
        #             logging.debug('energy_metrics no data found' )
        #             metrics_value.append(0.0)
        #             metrics_unit.append("NA")
        #             metrics_compare_percent.append(0.0)
        #             metrics_trend.append("NA")
        #             metrics_trend_status.append("NA")
        #
        # return metrics_value, metrics_unit, metrics_compare_percent, metrics_trend, metrics_trend_status

    # def parseBuildings (self, data = None ):
    #     buildings = []
    #     for bldg in data:
    #         logging.debug("parseBuildings  bld %s " %bldg)
    #         if '_' not in bldg['src'] :
    #             #building['id'] = bldg['src']
    #             buildings.append(bldg['src'])
    #     return buildings

    def getBuildings (self ):
        # curl -H "maxauth: $max_token" "${MAXIMO_URL}/maximo/oslc/os/mxasset?oslc.select={*}&oslc.where=assettype=\"PROD_SUPPORT\"" | jq .
        # q_endpoint = self.url + "/maximo/oslc/os/mxasset?oslc.select=assetmeter&oslc.where=assettag=" + "BUILDING"
        # /os/mxasset?oslc.where=assettype="VAN"
        # TODO, the following call seems to work better
        buildings = []
        q_endpoint = self.url + "/maxrest/rest/mbo/ASSET/?TEMPLATEID=" + self.template_id + "&_lid=" + self.username + "&_lpwd=" + self.password + "&_format=json" # &siteid=DENVER
        # headers = { "maxauth": self.token }
        headers = { "maxauth": self.token }
        print("q_endpoint")
        print(q_endpoint)
        print("cookies")
        print(self.cookies)
        print("headers")
        print(headers)
        res = requests.get(q_endpoint, cookies=self.cookies, headers=headers) # , headers=headers)
        r_data = res.json()
        if "ASSETMboSet" in r_data.keys():
            for r in r_data['ASSETMboSet']['ASSET']:
                buildings.append(r['Attributes']['ASSETNUM']['content'])
        print(buildings)
        # returns an array of asset ids
        return buildings

    # def getBuildingData(self):
    #
    #     "${MAXIMO_URL}/maximo/oslc/os/mxasset?oslc.select=assetmeter&where=assetnum=2112&_lid=wilson&_lpwd=wilson"

    # def authRealm ( self) :

    def execute(self, df, start_ts = None,end_ts=None,entities=None):

        entity_type = self.get_entity_type()
        self.db = entity_type.db
        encoded_body = json.dumps(self.body).encode('utf-8')
        encoded_headers = json.dumps(self.headers).encode('utf-8')

        # This class is setup to write to the entity time series table
        # To route data to a different table in a custom function,
        # you can assign the table name to the out_table_name class variable
        # or create a new instance variable with the same name

        if self.out_table_name is None:
            table = entity_type.name
        else:
            table = self.out_table_name

        schema = entity_type._db_schema

        #  "url" is the tenantid for Maximo that is used to build the uri to call the Maximo Rest service.
        # logging.debug('refresh token %s' %self.refreshToken() )

        # if self.realm_token:
        #     cookies = dict( LtpaToken2=self.realm_token )
        # else:
        #     cookies = dict()

        if self.realm:
            logging.debug("setting cookies for realm auth")
            # user will need to pass in realm creds
            auth=(self.realm_user, self.realm_pass)
            r = requests.get(self.url + "/maximo/oslc", auth=auth)
            print(auth)
            cookies = r.cookies.get_dict()
            print("url")
            print(self.url)
            print("cookies")
            print(cookies)
            if 'LtpaToken2' in cookies.keys():
                logging.debug("cookie received")
                self.realm_token = cookies['LtpaToken2']
                self.cookies = dict( LtpaToken2=self.realm_token )
            else:
                logging.debug("no cookie received")
                self.cookies = dict()
        else:
            logging.debug("no realm auth requested")
            self.cookies = dict()

        buildings = self.getBuildings()
        for building in buildings:
            logging.debug('building name %s' %building )

        # Column('building',String(50)),
        # Column('energy_value',Float()),
        # Column('energy_unit',String(50)),
        # Column('temperature',Float()),


        rows = len(buildings)
        logging.debug('rows %s ' %rows)
        response_data = {}
        (metrics,dates,categoricals,others) = self.db.get_column_lists_by_type(
            table = table,
            schema= schema,
            exclude_cols = []
        )
        for m in metrics:
            logging.debug('metrics %s ' %m)
            response_data[m] = np.random.normal(0,1,rows)
            logging.debug('metrics data %s ' %response_data[m])

        for d in dates:
            logging.debug('dates %s ' %d)
            response_data[d] = dt.datetime.utcnow() - dt.timedelta(seconds=15)
            logging.debug('dates data %s ' %response_data[d])

        '''
        # Create Numpy array using Maximo energy usage data
        '''

        # spi:metername
        # meter_names = np.array(["TEMP-F", "ENERGY"])

        # TODO, lets assume all buildings track energy and temperature
        ids = []
        vals = []
        dates = []
        for b in buildings:
            meters = self.getMeters(b)
            meter_names = np.array([m['spi:metername'] for m in meters])
            # measureunitids = np.array([m['spi:measureunitid'] for m in meters if 'spi:measureunitid' in m.keys() ])
            for m in meters:
                # TODO, all meters will likely not be updated at the same freqency
                if "TEMP" in m['spi:metername']:
                    print("Temp found for building: " + b)
                    # if 'spi:measureunitid' in m.keys():
                    #     ids.append(m['spi:measureunitid'])
                    # else:
                    #     ids.append("N/A")
                    if "spi:lastreading" in m.keys():
                        vals.append(m["spi:lastreading"])
                    if "spi:lastreadingdate" in m.keys():
                        dates.append(m["spi:lastreadingdate"])
            # measureunitids = np.array(ids)

        # buildings = ["2112", "2113"]
        response_data['building'] = np.array(buildings)
        response_data['temperature_unit'] = np.array(["F"] * len(vals)) #np.array(["F", "F"])
        response_data['temperature'] = np.array(vals) #np.array([73.2 , 81.4])
        # response_data['energy_unit'] = np.array(["KW"] * len(meters)) # np.array(["KW", "KW"])
        # response_data['energy_value'] = np.array([16.3 , 235.0])

        # metrics_value, metrics_unit, metrics_compare_percent, metrics_trend, metrics_trend_status = self.getMeters ( buildings = buildings)

        # logging.debug("length metrics_value %d" %len(metrics_value) )
        # logging.debug("length metrics_unit %d" %len(metrics_unit) )
        # logging.debug("length metrics_compare_percent %d" %len(metrics_compare_percent) )
        # logging.debug("length metrics_trend %d" %len(metrics_trend) )
        # logging.debug("length metrics_trend_status %d" %len(metrics_trend_status) )
        logging.debug("length buildings %d" %len(buildings) )
        # response_data['energy_value'] = np.array( metrics_value )
        # response_data['energy_unit'] = np.array( metrics_unit )
        # response_data['energy_compare_percent'] = np.array( metrics_compare_percent )
        # response_data['energy_trend'] = np.array( metrics_trend )
        # response_data['energy_trend_status'] = np.array( metrics_trend_status )
        # response_data['building'] = np.array(buildings)

        ## TODO, not sure what the following values should be?
        response_data['devicetype'] = np.array(buildings)
        response_data['logicalinterface_id'] = np.array(buildings)
        response_data['eventtype'] = np.array(buildings)
        response_data['deviceid'] = np.array(buildings)
        response_data['format'] = np.array(buildings)
        response_data['logicalinterface_id'] = np.array(buildings)

        '''
        # Create a timeseries dataframe with data received from Maximo
        '''
        logging.debug('response_data used to create dataframe ===' )
        logging.debug( response_data)
        df = pd.DataFrame(data=response_data)
        logging.debug('Generated DF from response_data ===' )
        logging.debug( df.head() )
        df = df.rename(self.column_map, axis='columns')
        logging.debug('ReMapped DF ===' )
        logging.debug( df.head() )

        '''
        # Fill in missing columns with nulls
        '''
        required_cols = self.db.get_column_names(table = table, schema=schema)
        logging.debug('required_cols %s' %required_cols )
        missing_cols = list(set(required_cols) - set(df.columns))
        logging.debug('missing_cols %s' %missing_cols )
        if len(missing_cols) > 0:
            kwargs = {
                'missing_cols' : missing_cols
            }
            entity_type.trace_append(created_by = self,
                                     msg = 'http data was missing columns. Adding values.',
                                     log_method=logger.debug,
                                     **kwargs)
            for m in missing_cols:
                if m==entity_type._timestamp:
                    df[m] = dt.datetime.utcnow() - dt.timedelta(seconds=15)
                elif m=='devicetype':
                    df[m] = entity_type.logical_name
                else:
                    df[m] = None

        '''
        # Remove columns that are not required
        '''
        df = df[required_cols]
        logging.debug('DF stripped to only required columns ===' )
        logging.debug( df.head() )

        '''
        # Write the dataframe to the IBM IOT Platform database table
        '''
        self.write_frame(df=df,table_name=table)
        kwargs ={
            'table_name' : table,
            'schema' : schema,
            'row_count' : len(df.index)
        }
        entity_type.trace_append(created_by=self,
                                 msg='Wrote data to table',
                                 log_method=logger.debug,
                                 **kwargs)
        return True

    '''
    # Create the IOT Platform Function User Interfact input arguements used to connect to the external REST Service.
    # These could be used to connect with any Rest Service to get IOT Data or any other data to include in your dashboards.
    '''
    @classmethod
    def build_ui(cls):
        '''
        Registration metadata
        '''
        # define arguments that behave as function inputs
        inputs = []
        inputs.append(ui.UISingle(name='username',
                              datatype=str,
                              description='Username for Maximo Instance',
                              tags=['TEXT'],
                              required=True
                              ))
        inputs.append(ui.UISingle(name='password',
                              datatype=str,
                              description='Password for Maximo Instance',
                              tags=['TEXT'],
                              required=True
                              ))
        inputs.append(ui.UISingle(name='request',
                              datatype=str,
                              description='HTTP Request type',
                              values=['GET','POST','PUT','DELETE']
                              ))
        inputs.append(ui.UISingle(name='url',
                                  datatype=str,
                                  description='request url use internal_test',
                                  tags=['TEXT'],
                                  required=True
                                  ))
        inputs.append(ui.UISingle(name='headers',
                               datatype=dict,
                               description='request url',
                               required = False
                               ))
        inputs.append(ui.UISingle(name='body',
                               datatype=dict,
                               description='request body',
                               required=False
                               ))
        # define arguments that behave as function outputs
        outputs=[]
        outputs.append(ui.UIStatusFlag(name='output_item'))
        return (inputs, outputs)
class customIfThenElse(BaseTransformer):
    """
    Set the value of the output_item based on a conditional expression.
    When the conditional expression returns a True value, return the value of the true_expression.
    Example:
    conditional_expression: df['x1'] > 5 * df['x2']
    true expression: df['x2'] * 5
    false expression: 0
    """

    def __init__(self, conditional_expression, true_expression, false_expression, output_item=None):
        super().__init__()
        self.conditional_expression = self.parse_expression(conditional_expression)
        self.true_expression = self.parse_expression(true_expression)
        self.false_expression = self.parse_expression(false_expression)
        if output_item is None:
            self.output_item = 'output_item'
        else:
            self.output_item = output_item

    def execute(self, df):
        c = self._entity_type.get_attributes_dict()
        df = df.copy()
        df[self.output_item] = np.where(eval(self.conditional_expression), eval(self.true_expression),
                                        eval(self.false_expression))
        return df

    @classmethod
    def build_ui(cls):
        # define arguments that behave as function inputs
        inputs = []
        inputs.append(UIExpression(name='conditional_expression', description="expression that returns a True/False value, \
                                                eg. if df['temp']>50 then df['temp'] else None"))
        inputs.append(UIExpression(name='true_expression', description="expression when true, eg. df['temp']"))
        inputs.append(UIExpression(name='false_expression', description='expression when false, eg. None'))
        # define arguments that behave as function outputs
        outputs = []
        outputs.append(UIFunctionOutSingle(name='output_item', datatype=bool, description='Dummy function output'))

        return (inputs, outputs)

    def get_input_items(self):
        items = self.get_expression_items([self.conditional_expression, self.true_expression, self.false_expression])
        return items