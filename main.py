# Memphis Bamboo Build Plans 1.0
# Author: ShubhamS
"""This module is responsible for triggering bamboo build plans for driver/adapter.

This triggers the bamboo build plan.

  Typical usage example:
  $ python BambooBuildPlans.py
  And follow the on-screen instructions.
"""
import os
from json import load

import codecs
import urllib
import requests
import getpass
import base64
import xml.etree.cElementTree as et
import webbrowser

from atlassian import Bamboo

class BambooBuildPlans:

    def __init__(self, input_args: dict):
        self.input_args = input_args
        self.project = input_args['inBambooConfigs']['inProjectKey']
        # self.Packageproject = input_args['inBambooConfigs']['inPackageProjectKey']
        # self.FTproject = input_args['inBambooConfigs']['inFTProjectKey']
        self.driver_label = input_args['inBambooConfigs']['inDriverLabel']
        self.core_label = input_args['inBambooConfigs']['inCoreLabel']
        self.sen_label = input_args['inBambooConfigs']['inSENLabel']
        self.windows_build_configs = input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inPlatform'] + " " + \
                                     input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inCompiler'] + " " + \
                                     input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inConfiguration']
        self.linux_build_configs = input_args['inBambooConfigs']['inBuildConfigs']['Linux']['inPlatform'] + " " + \
                                   input_args['inBambooConfigs']['inBuildConfigs']['Linux']['inCompiler'] + " " + \
                                   input_args['inBambooConfigs']['inBuildConfigs']['Linux']['inConfiguration']
        self.osx_build_configs = input_args['inBambooConfigs']['inBuildConfigs']['OSX']['inPlatform'] + " " + \
                                 input_args['inBambooConfigs']['inBuildConfigs']['OSX']['inCompiler'] + " " + \
                                 input_args['inBambooConfigs']['inBuildConfigs']['OSX']['inConfiguration']
        self.branch_name = input_args['inBambooConfigs']['inBranchName']

    def build(self):
        # Ask user to login with Bigsight credentials and trigger the build plan
        atlassian_user = "shyamj"
        atlassian_password = "Ganesh24$"

        user_pass = atlassian_user + ':' + atlassian_password
        base_64_val = base64.b64encode(user_pass.encode()).decode()
        bamboo_url = os.environ.get("http://bergamot3.lakes.ad:8085", "http://bergamot3.lakes.ad:8085")

        # Creates the bamboo object with user credentials for sending http requests
        bamboo = Bamboo(url=bamboo_url, username=atlassian_user, password=atlassian_password)
        url = self.get_project_url(base_64_val)
        if not url == None:
            if len(self.windows_build_configs) > 2:
                branch_info = bamboo.get_branch_info(self.get_plan_key(url, base_64_val, self.windows_build_configs),
                                                 self.branch_name)
                branch_key = branch_info['key']
                bamboo.execute_build(branch_key, **self.get_params())
                print('Bamboo build is started for ' + self.branch_name.split(' ')[0] + ' ODBC in windows platform')
                self.open_browser(branch_info['latestResult']['link']['href'])
                return True

            if len(self.linux_build_configs) > 2:
                branch_info = bamboo.get_branch_info(self.get_plan_key(url, base_64_val, self.linux_build_configs),
                                                 self.branch_name)
                branch_key = branch_info['key']
                bamboo.execute_build(branch_key, **self.get_params())
                print('Bamboo build is started for ' + self.branch_name.split(' ')[0] + ' adapter in linux platform')
                self.open_browser(branch_info['latestResult']['link']['href'])
                return True
            if len(self.osx_build_configs) > 2:
                branch_info = bamboo.get_branch_info(self.get_plan_key(url, base_64_val, self.osx_build_configs),
                                                 self.branch_name)
                branch_key = branch_info['key']
                bamboo.execute_build(branch_key, **self.get_params())
                print('Bamboo build is started for ' + self.branch_name.split(' ')[0] + ' adapter in osx platform')
                self.open_browser(branch_info['latestResult']['link']['href'])
                return True
        else:
            print(self.project + ' project not found. Please verify the project key.')
            return False

    def get_plan_key(self, url, base_64_user_pass, build_configs):
        url += '?expand=plans&max-result=100'
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        tree = et.fromstring(response.content)

        for child in tree.iter('*'):
            try:
                if child.attrib.get('shortName').__contains__(build_configs):
                    return child.attrib.get('key')
            except:
                continue

    def get_project_url(self, base_64_user_pass):
        url = "http://bergamot3.lakes.ad:8085/rest/api/latest/project/" + self.project
        if self.project != "":
            return url
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        tree = et.fromstring(response.content)

        found_proj = False
        for child in tree.iter('*'):
            if found_proj:
                return child.attrib.get('href')
            try:
                if child.attrib.get('key').__contains__(self.project):
                    found_proj = True
                    key = child.attrib.get('key')
            except:
                continue

    def get_params(self):
        params = {
            "BOOSTER_LABEL": "__head__",
            "DRV_LABEL": self.driver_label,
            "CORE_LABEL": self.core_label,
            "SEN_LABEL": self.sen_label,
            "DYNAMIC_LINKING": 0,
            "RETAIL": 0,
            "PRODUCT_LABEL": "BAMBOO_DRV_LABEL",
            "DISBALE_PARENT_MATCH": 0,
            "TARGET": "release",
            "MEMORY_TEST": 1,
            "AFL": 0,
            "VERACODE": 0,
            "CODE_ANALYSIS": 0,
            "COMPILER": 'vs2013',
            "BUILD_SOURCE": 'w2012r2'

        }
        return params

    def open_browser(self, url: str):
        job_id = int(url[len(url) - 1]) + 1
        url = url[0: len(url) - 1] + str(job_id)
        url = url.replace('rest/api/latest/result', 'browse')
        webbrowser.open(url, new=2)


def run_bamboo_adapter_build(input_args: dict):
    print("Building driver/adapter on bamboo...BEGIN")
    bamboo_build = BambooBuildPlans(input_args)
    # run_build_driver_as_server(input_args)
    if bamboo_build.build():
        print("Please go through the logs generated on bamboo for further reference.")
    else:
        print("Please check the input parameters and try again.")


def main():
    input_json_file = 'user_input.json'
    if not os.path.exists(input_json_file):
        print("IMPORTANT: Please ensure to modify user_input.json as per your "
              "needs prior to running this.")
        input_json_file = input("Please enter the full path to the input json "
                                "file (e.g., C:\\user_input.json): ")
    f = open(input_json_file)
    run_bamboo_adapter_build(load(f))
    print(plan_results(self.project, self.get_plan_key))
    #data = urllib.request.urlopen("http://bergamot3.lakes.ad:8085/browse/TSTFOMEM-WIN2012R26432M104-21/artifact/JOB/Logs/build.txt")  # it's a file like object and works just like a file
    #path = data.readlines()[1].strip().decode('utf-8')
    #print(path.replace('oak','oak.simba.ad'))

if __name__ == '__main__':
    main()
