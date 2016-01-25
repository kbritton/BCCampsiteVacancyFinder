import time
from lxml import html 
import requests
import boto3

# pip install lxml && pip install requests
# http://docs.python-requests.org/en/latest/user/quickstart/

# build a Lambda package
# python -m pip install -U lxml -t /Users/kenbritton/Desktop/FindCampsiteVacancies
# python -m pip install -U requests -t /Users/kenbritton/Desktop/FindCampsiteVacancies

### Sites
# 1. Gordon Bay Group Site - Cowichan Lake
# 2. Cowichanlake.ca
# 3. Mussel Beach?
# 4. sitesandtrailsbc.ca
# 5. Newcastle (boat access only)
# 6. Kokanee creek
# 7. Wells Gray - booked July 23-Aug 4; Aug 1-4
# 8. French beach (van island) - July 11-15; Aug 14-17
# 10. Hornby?

def lambda_handler(event, context):

    emailString = ""

    ## 2. get cookies
    cookies = get_cookies()
    print(cookies)

    ## 3. pull values from pages
    # emailString += scrape(cookies,'60ee1cec-7fcb-4681-bbe2-c2daf9bd4a67','6b8338f5-76f0-457b-a938-b8eabbddb0cb','49229730-7666-415e-a150-861fb0a13d06','Sasquatch - Group Site G1')
    # emailString += "\n"
    # emailString += scrape(cookies,'7446b3fd-59e4-412c-a4f2-05552bd31f6d','efc77946-af1d-4401-a09f-3b5be777142f','Mabel Lake - Group Site G1')
#     emailString += "\n"
    emailString += scrape(cookies,'88d19740-376f-44b1-b6c7-1ce71e7bfacc','cf89757b-e7c2-4522-ae4c-e619f6136dce','447f96af-0a67-4fa7-bd0f-c4154e0793bd','Kokanee Creek - Group Site G1')
    emailString += "\n"
#     emailString += scrape(cookies,'88d19740-376f-44b1-b6c7-1ce71e7bfacc','8face699-98ec-4e71-91fd-b0d57dcd3bb2','Kokanee Creek - Group Site G2')
    print(emailString)
    
    ## 4. publish an SNS message
    #send_sns(emailString)
    
def get_cookies():
    
    resp = requests.get('https://secure.camis.com/DiscoverCamping/', timeout=10)
    return resp.cookies
    
def chooseGroupsite(cookies, locationId, mapId, resourceId):
    
    # set reservation properties
    payload1 = {
        'resType': 'Group',
        #'equipment':'',
        #'equipmentSub':'null',
        #'vehicleLength':'',
        #'tentPads':'',
        #'ReservableOnline_incl':'on',
        'arrDate':':2016-07-1',
        'nights':'3',
        #'apId':'null',
        #'locId':locationId,
        #'mapId':mapId,
        #'rceId':resourceId
    }
    headers = {'Referer':'https://secure.camis.com/DiscoverCamping/KokaneeCreekProvincialPark/GroupSites?Map'}
    
    resp1 = requests.post("https://secure.camis.com/DiscoverCamping/ResInfo.ashx", data=payload1, cookies=cookies, headers=headers)
    print(resp1.content)
    
    # set the selected resource
    payload2 = {
        'type': 'Resource',
        'id':resourceId
    }
    resp2 = requests.post("https://secure.camis.com/DiscoverCamping/Details.ashx", data=payload2, cookies=cookies, headers=headers)
    print(resp2.content)
    
def scrape(cookies, locationId, mapId, resourceId, siteName):
    
    emailString = "%s\n" % (siteName)
    
    ## 1. set GroupCampsite preference
    chooseGroupsite(cookies, locationId, mapId, resourceId)
    
    ## 2. view availability
    resp = requests.get("https://secure.camis.com/DiscoverCamping/RceAvail.aspx?locId=%s&mapId=%s&rceId=%s&nav=6" % (locationId, mapId, resourceId), cookies=cookies, timeout=10)
    content = resp.content
    print(content)

    # # 3. read local HTML file
    # file = open('result.html', 'r')
    # content = file.read()
    #print(content)

    tree = html.fromstring(content)
    calendars = tree.xpath('//table[@title="Calendar"]')
    for cal in calendars:
        month = cal.xpath('.//table[@class="cal"]/tr/td/text()')[0]
        emailString += "\n" + month + "\n"
        dates = cal.xpath('.//td[@class="avail"]/text()')
        for date in dates:
            emailString += date + "\n"
    
    return emailString
    
def send_sns(emailString):
    
    client = boto3.client('sns')
    response = client.publish(
        TopicArn='arn:aws:sns:us-east-1:409664833508:kbritton_campsite_available',
        Message=emailString,
        Subject='Campsite Search Results'
    )
    return response

if __name__ == '__main__': lambda_handler(None,None)