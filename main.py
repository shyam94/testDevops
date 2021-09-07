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
from socket import *

import zipfile
import shutil
import os, stat
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import smtplib
from os.path import basename
import sys

from atlassian import Bamboo

class DrMemoryTask:

    def __init__(self, username, password, email, outlook_password, shared_folder_path, input_args: dict):
        self.input_args = input_args
        self.driver_label = input_args['inBambooConfigs']['inDriverLabel']
        self.core_label = input_args['inBambooConfigs']['inCoreLabel']
        self.sen_label = input_args['inBambooConfigs']['inSENLabel']
        self.windows_build_configs = input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inPlatform'] + " " + \
                                     input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inCompiler'] + " " + \
                                     input_args['inBambooConfigs']['inBuildConfigs']['Windows']['inConfiguration']
        self.branch_name = input_args['inBambooConfigs']['inBranchName']
        self.excludeCompile = input_args['ExcludeCompilation']
        self.atlassian_user = username
        self.atlassian_password = password
        self.receiver_email = email
        self.outlook_password = outlook_password
        self.shared_folder_path = shared_folder_path

    def build(self, projectKey):
        user_pass = self.atlassian_user + ':' + self.atlassian_password
        base_64_val = base64.b64encode(user_pass.encode()).decode()
        bamboo_url = os.environ.get("http://bergamot3.lakes.ad:8085", "http://bergamot3.lakes.ad:8085")

        # Creates the bamboo object with user credentials for sending http requests
        bamboo = Bamboo(url=bamboo_url, username=self.atlassian_user, password=self.atlassian_password)
        url = "http://bergamot3.lakes.ad:8085/rest/api/latest/project/" + projectKey
        if not url == None:
            if len(self.windows_build_configs) > 2:
                #self.get_plan_key(url, base_64_val, self.windows_build_configs)
                branch_info = bamboo.get_branch_info(
                              "BULDOMEM-WIN2012R2VS000201332" if projectKey == "BULDOMEM" else "TSTFOMEM-WIN2012R26432M",
                              self.branch_name)
                branch_key = branch_info['key']
                #bamboo.execute_build(branch_key, **self.get_params())
                #print('Bamboo build is started for ' + self.branch_name.split(' ')[0] + ' ODBC in windows platform')
                #url = update_Job_Id(branch_info['latestResult']['link']['href'])
                url = branch_info['latestResult']['link']['href']
                #self.open_browser(url)
                #self.check_plan_status(url,base_64_val)
                if projectKey == "TSTFOMEM":
                    data = urllib.request.urlopen(url.replace('rest/api/latest/result', 'browse') + "/artifact/JOB/Logs/build.txt")
                    path = data.readlines()[1].strip().decode('utf-8')
                    path = path.replace('oak', 'oak.simba.ad')
                    self.get_logs(path)

                return True
        else:
            print(self.project + ' project not found. Please verify the project key.')
            return False

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
        url = url.replace('rest/api/latest/result', 'browse')
        webbrowser.open(url, new=2)

    def check_plan_status(self, url, base_64_user_pass):
        payload = ""
        headers = {
            'Authorization': "Basic " + base_64_user_pass
        }
        if url.find("BULD") != -1:
            print("Compile plan (with MEM) is running and in progress")
        else:
            print("Functional test plan (with DrMemory) is running and in progress")
        status = ""
        while True:
            response = requests.request("GET", url, data=payload, headers=headers)
            root = et.fromstring(response.content)
            for buildState in root.iter('buildState'):
                status = buildState.text
            if status != "Unknown":
                break
            time.sleep(60)
        if status == "Failed" and url.find("BULD") != -1:
            print("Compile plan failed hence the script will stop")
            exit()
        print("Bamboo Plan Execution Finished with result: " + status)

    def get_logs(self,filePath):
        remotezip = self.shared_folder_path + filePath[filePath.find("archive\\") + 7:] + "\\log.zip" 
        remotezip = repr(remotezip)
        os.chmod(remotezip,0o777)
        zip = zipfile.ZipFile(remotezip)
        files = []
        for fn in zip.namelist():
            if fn.endswith("results.txt"):
                file = zip.read(fn).decode("utf-8")
                fileName = sys.argv[1] + "\\" + fn[fn.find("memoryReport/") + 13:fn.find("/DrMemory-Touchstone.exe")]
                f = open(fileName, "w+")
                found = 0
                for line in file.split("\n"):
                    if "# 0 " in line and "\\drivers\\memphis" in line:
                        errors = "\n" + prevLine
                        found = 1
                    if found == 1:
                        if line != "\r":
                            errors += line
                            continue
                        else:
                            found = 0
                            f.write(errors)
                    prevLine = line
                if(os.stat(f.name).st_size > 0):
                    files.append(fileName)
                f.close()

        self.send_mail(files)

    def send_mail(self,attachments):
        SERVER = "smtp-mail.outlook.com"
        FROM = "sjoshi@magnitude.com"
        TO = [self.receiver_email]  # must be a list

        # Prepare actual message
        msg = MIMEMultipart()
        msg['From'] = FROM
        msg['To'] = COMMASPACE.join(TO)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "DrMemory Report"

        msg.attach(MIMEText("Hey!\r\n Here is your memory report from DrMemory.\r\n Thanks."))
        # message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\
        for file in attachments or []:
            with open(file, "rb") as report:
                part = MIMEApplication(
                    report.read(),
                    Name=basename(file)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
            msg.attach(part)

        server = smtplib.SMTP(SERVER, 587)
        server.connect(SERVER, 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("sjoshi@magsw.com", self.outlook_password)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()

        """ % (FROM, ", ".join(TO), SUBJECT, TEXT) """

        # Send the mail

def update_Job_Id(url):
    job_id = url.split("-")[-1]
    url = url[0: len(url) - len(job_id)] + str(int(job_id) + 1)
    return url

def run_bamboo_adapter_build(input_args: dict):
    print("Building driver/adapter on bamboo...BEGIN")
    bamboo_build = DrMemoryTask(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], input_args)
    projectKeys = ["TSTFOMEM"]
    if not bamboo_build.excludeCompile:
        projectKeys.insert(0,"BULDOMEM")
    for projectKey in projectKeys:
        if bamboo_build.build(projectKey):
            print("Please go through the logs generated on bamboo for further reference.")
        else:
            print("Please check the input parameters and try again.")

def main():
    input_json_file = sys.argv[1] + '\\user_input.json'
    if not os.path.exists(input_json_file):
        print("IMPORTANT: Please ensure to modify user_input.json as per your "
              "needs prior to running this.")
        input_json_file = input("Please enter the full path to the input json "
                                "file (e.g., C:\\user_input.json): ")
    f = open(input_json_file)
    run_bamboo_adapter_build(load(f))

if __name__ == '__main__':
    main()
