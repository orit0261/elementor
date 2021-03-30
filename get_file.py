import csv
import os

import wget
import requests

from log import Trace

APPID = 'bdca18625acc67cfdac99a04c3361f837c33ae70720dbd030625241c54f5f78c'
API_URL = 'https://www.virustotal.com/vtapi/v2/url/report'

#from sqlalchemy import create_engine
#db = create_engine('postgresql+psycopg2://postgres:orit0261@localhost:5432/dev')


def set_total(key,total_dic):
    total_dic[key]=total_dic[key]+1

def get_response(surl):
    try:
        params = {'apikey': APPID, 'resource': surl}
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            scans = dict(response.json())['scans']
            risk_found = False
            category = 'safe'
            total_dict={'malicious':0,'phishing site':0,'malware':0,'clean site':0,'unrated':0}
            for i in scans:
                set_total(scans[i]['result'],total_dict)

                if not risk_found and \
                        (('malicious' in scans[i]['result'].lower()) \
                         or ('phishing' in scans[i]['result'].lower()) \
                         or ('malware' in scans[i]['result'].lower())):
                    category = 'risk'
                    risk_found = True
                # when risk found loop terminated
                #else:
                #    response.close()
                #    break
        else:
            print('error in response',response.status_code)
            raise ('error in response number', response.status_code)
    except:
        category = None
        print('url doesnt exists')

    #return Trace.MakeResponse(db,api_name="scan url",
    #                          trace_id=response.headers.get('Trace-Id'),
    #                          status=str(response.status_code), message="No documents found",
    #                          request_json=str(response),
    #                          response_json='')

    #db.session.close()
    return category


# download csv file from sever
filename = 'request1.csv'
if os.path.exists(filename):
    os.remove(filename)
wget.download("https://elementor-pub.s3.eu-central-1.amazonaws.com/Data-Enginner/Challenge1/request1.csv")
rows = []

with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting each data row one by one
    for row in csvreader:
        # send call to api with url
        print("%10s" % row, '=', get_response(row[0].strip()))
