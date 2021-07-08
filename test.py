from jira import JIRA
import argparse
import sys,ast
"""jiraOptions = {'server': "https://jira.magnitude.com", 'verify':False}

jira = JIRA(options=jiraOptions, basic_auth=(
    "pcheemakurthi", "Gnca9a059$") )
    
issue=jira.issue('MPHJ-2280')
print(issue.fields.summary)
issue_dict = {
    'project': {'id': '14301'},
    'summary': 'New issue from jira-python',
    'issuetype': {'id': '5'},
    'parent': {'id': '228307'}
}
new_issue = jira.create_issue(fields=issue_dict)

new_issue.delete()



#issue = jira.issue('MPHJ-2076')
#try:
    #jira = JIRA('https://jira.magnitude.com')
    #auth_jira = JIRA(basic_auth=('szhang@magnitude.com', 'IoWDdF1YXSYhHF2MJlsSEBCA'))
    #jira = JIRA(options=jiraOptions, basic_auth=("szhang@magnitude.com", "IoWDdF1YXSYhHF2MJlsSEBCA"))
    #issue = jira.issue('MPHJ-2076')
    #summary=issue.fields.summary    
    #print(summary)
#except:
 #   print("Connection refused by the server..")"""
class JiraOperations:
    conmapProjectId="15904"
    subtaskProjectId="14301"
    allPlatforms={
    "windows": "10503",
    "osx":"10505",
    "linux":"10504",
    "jdbc":"13006"
    }
    allCustomers={
    "qlik": "12030",
    "rstudio":"12033",
    "acl":"12011",
    "ibm":"12704",
    "retail":"13007"
    }
    parentIds={
    "amazon":"111478"
    }
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.jiraOptions={'server': "https://jira.magnitude.com",'verify':False}
        
    def createSubTask(self,projectId,summary,parentId):
        issue_values={'project':{'id': projectId}, 'summary':summary,'issuetype': {'id' : '5' },'parent': {'id': parentId }}
        jira=self.connect(issue_values)
        return jira.create_issue(fields=issue_values)
        
    def createConmapTask(self,driverName,summary,releaseVersion,platforms,customers):
        issue_values={'project':{'id': self.conmapProjectId}, 'summary':summary,'issuetype': {'id' : '10902' },'parent': {'id': self.parentIds[driverName]}, 'customfield_11008': releaseVersion}
        
        #print(platforms[1])
        #print(customers)
        customerArray=list()
        for customer in customers:
            print(customer)
            customerDict = dict()
            customerDict["id"]=self.allCustomers[customer]
            customerArray.append(customerDict)
        issue_values["customfield_13915"]=customerArray
        
        customerPlatforms=list()
        for platform in platforms:
            tempDict = dict()
            tempDict["id"]=self.allPlatforms[platform]
            customerPlatforms.append(tempDict) 
        issue_values["customfield_11003"]=customerPlatforms
            
        jira=self.connect(issue_values)
        return jira.create_issue(fields=issue_values)
        
    
    def connect(self,issue_values):
        return JIRA(options=self.jiraOptions,basic_auth=(self.username,self.password))
        
platformArgs = sys.argv[6].split(',')
"""print(arr1[1])
print(arr1)
print(type(arr1[1]))"""

customerArgs = sys.argv[7].split(',')
"""print(arr2[1])
print(arr2)
print(type(arr2[1]))"""

"""inputList = ast.literal_eval(sys.argv[7])
print(type( inputList))
print(inputList) 
print(type(inputList[0]))"""

jira=JiraOperations(sys.argv[1],sys.argv[2])
issue=jira.createConmapTask(sys.argv[3],sys.argv[4],sys.argv[5],platformArgs,customerArgs)
print(issue)

"""jira=JiraOperations("pcheemakurthi","Gnca9a059$")
issue=jira.createConmapTask("amazon","New sub issue from jira-python","1.6.34",["windows",],["qlik"])
#issue=jira.createSubTask("14301","New sub issue from jira-python","5","228307")
print(issue)
parser = argparse.ArgumentParser()
parser.add_argument('-u','--username',"username",help="Username to connect with jira", type = str)
parser.add_argument('-p',"password",help="Password of your username", type = str)
parser.add_argument('-d',"DriverName",help="Driver for which you want to create CONMAP", type = str)
parser.add_argument('-s',"Summary",help="Summary of CONMAP TASK", type = str)
parser.add_argument('-r',"ReleaseVersion",help="ReleaseVersion of CONMAP Task", type = str)
parser.add_argument('-p',"Platforms",help="Platforms for the release", )
parser.add_argument('-c',"Customers",help="Customers for the release", type = str)

args=parser.parse_args()
jira=JiraOperations(args.username,args.password)
issue=jira.createConmapTask(args.DriverName,args.Summary,args.ReleaseVersion,args.Platforms,args.Customers)
print(issue)"""



 