import os
import re
import sys
import urllib3
import requests
import pandas as pd
from json import dumps
from typing import final
from datetime import datetime, timedelta


print("""
*****************************************
* JIRA TestCycle creation tool          *
* based on Python 3.10                  *
* maintained by: vitvasilyuk@gmail.com  *
*****************************************
""")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    print(f'ProjectKey: {str(sys.argv[1])}\n'
          f'JiraUser:   {str(sys.argv[2])}\n'
          f'JiraPass:   {"*****" if str(sys.argv[3]) else "N/A"}\n')
except IndexError as ex:
    raise Exception(f'Arguments not passed !')

suites_csv_path: final(str) = os.getcwd()+'/../../test_model/allure-report/data/suites.csv'
jira_server: final(str) = 'https://jira.your_server.com/rest'
jira_project_key: final(str) = str(sys.argv[1])
jira_username: final(str) = str(sys.argv[2])
jira_password: final(str) = str(sys.argv[3])

resp = requests.post(url=f'{jira_server}/auth/1/session',
                     headers={"Authorization": "application/json",
                              "Content-Type":  "application/json",
                              "User-Agent":    "Jenkins"},
                     verify=False,
                     data=f'{{"username": "{jira_username}",'
                            f'"password": "{jira_password}"}}')

if resp.status_code not in [200, 201]:
    raise Exception(f'Receive bad status on Authorization: {resp.status_code}')

cookie = resp.cookies

df = pd.read_csv(suites_csv_path, sep=',')
df = df[['Name', 'Status']]
df = df.rename({
    'Name': 'testCaseKey',
    'Status': 'status'
}, axis=1)
try:
    df['testCaseKey'] = df['testCaseKey'].apply(lambda x: re.fullmatch(r'\((.+)\) - .+', x).group(1))
    df = df.groupby('testCaseKey')['status'].apply(lambda x: 'Pass' if (x == 'passed').all() else 'Fail').reset_index()
except AttributeError as err:
    raise Exception(f'There are tests with a missing JIRA key !!\n'
                    f'Can not create a TestCycle !!')

body = dumps({
    "projectKey": jira_project_key,
    "name": f"Jenkins Auto Create [{(datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d _ %H:%M')}]",
    "items": df.to_dict(orient='records'),
    "status": "Done"
})

resp = requests.post(url=f'{jira_server}/atm/1.0/testrun',
                     headers={"Authorization": "application/json",
                              "Content-Type":  "application/json",
                              "User-Agent":    "Jenkins"},
                     cookies=cookie,
                     verify=False,
                     data=body)

if resp.status_code not in [200, 201]:
    raise Exception(f'Receive bad status on TestCycle creation: {resp.status_code}')

print(f'JIRA TestCycle [{resp.json()["key"]}] has been created !!\n'
      f'link: https://jira.your_server.com/secure/Tests.jspa#/testPlayer/{resp.json()["key"]}')
