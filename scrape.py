
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import re


# In[82]:


page = urlopen("https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations_Amazon_Simple_Storage_Service.html")


# In[83]:


beautsoup = soup(page, "html.parser")
apiEndpoints = beautsoup.find_all('li',{'class':'listitem'})


# In[84]:


for endpoint in apiEndpoints:
    eachPageName = endpoint.a["href"][2:len(endpoint.a["href"])-5]
    attributeValue='#'+eachPageName+'_ResponseSyntax'
    #print(attributeValue)
    #print("https://docs.aws.amazon.com/AmazonS3/latest/API/"+eachPageName)
    eachPageURI = "https://docs.aws.amazon.com/AmazonS3/latest/API/"+eachPageName
    print(eachPageURI)
    eachPage = urlopen(eachPageURI)
    #print(eachPage)
    nestedPageSoup = soup(eachPage, "html.parser")
    responseHeading=nestedPageSoup.find_all('a',{'href':attributeValue})
    #print(responseHeading)
    for eachColumn in responseHeading:
        #eachColumn= item.a
        print(eachColumn.get_text())
    #responseHeading=nestedPageSoup.find_all("a", href ="#API_CompleteMultipartUpload_ResponseSyntax")
    #print(responseHeading)
    #print(nestedPageSoup.find_all(re.compile("\w")))
    #responseColumns = nestedPageSoup.find_all('div',{'class':'variablelist'})
    #print(responseColumns[1])
