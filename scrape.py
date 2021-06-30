from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import re
page = urlopen("https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations_Amazon_Simple_Storage_Service.html")
soup = BeautifulSoup(page, "html.parser")
apiEndpoints = soup.find_all('li',{'class':'listitem'})
for endpoint in apiEndpoints:
    eachPageName = endpoint.a["href"][2:]
    #print("https://docs.aws.amazon.com/AmazonS3/latest/API/"+eachPageName)
    eachPageURI = "https://docs.aws.amazon.com/AmazonS3/latest/API/"+eachPageName
    eachPage = urlopen(eachPageURI)
    #print(eachPage)
    nestedPageSoup = BeautifulSoup(eachPage, "html.parser")
    #print(nestedPageSoup)
    #print(nestedPageSoup.find_all(re.compile("\w")))
    responseColumns = nestedPageSoup.find_all('div',{'class':'variablelist'})
    print(responseColumns[1])