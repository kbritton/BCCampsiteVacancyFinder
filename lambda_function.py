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

    emailString = "Search Results: Sasquatch Group Site G1\n"

    ## 1. determine nav offset
    august = 8
    month = int(time.strftime("%m"))
    nav = str(august-month-1)
    print(nav)

    ## 2. get cookie
    r1 = requests.get('https://secure.camis.com/DiscoverCamping/Sasquatch/GroupCampingG1', timeout=10)
    aspSessionId = r1.cookies['ASP.NET_SessionId']
    print(aspSessionId)

    ## 3. get HTML body
    cookies = {'ASP.NET_SessionId' : aspSessionId}
    r2 = requests.get("https://secure.camis.com/DiscoverCamping/RceAvail.aspx?rceId=49229730-7666-415e-a150-861fb0a13d06&nav="+nav, cookies=cookies, timeout=10)
    content = r2.content
    #print(content)

    # # 3. read local HTML file
    # file = open('result.html', 'r')
    # content = file.read()
    #print(content)

    ## 4. extract availability
    tree = html.fromstring(content)
    calendars = tree.xpath('//table[@title="Calendar"]')
    for cal in calendars:
        month = cal.xpath('.//table[@class="cal"]/tr/td/text()')[0]
        emailString += "\n" + month + "\n"
        dates = cal.xpath('.//td[@class="filt" or @class="avail"]/text()')
        for date in dates:
            emailString += date + "\n"

    print(emailString)
    
    ## 5. publish an SNS message
    client = boto3.client('sns')
    response = client.publish(
        TopicArn='arn:aws:sns:us-east-1:409664833508:kbritton_campsite_available',
        Message=emailString,
        Subject='Campsite Search Results'
    )
    
    return response
    
if __name__ == '__main__': lambda_handler(None,None)