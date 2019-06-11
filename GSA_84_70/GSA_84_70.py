from bs4 import BeautifulSoup as bs
import requests
import json
import uuid
import pandas as pd

headers = headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
url_main_84 = requests.get('https://www.gsaelibrary.gsa.gov/ElibMain/scheduleSummary.do?scheduleNumber=84', headers=headers)
url_main_70 = requests.get('https://www.gsaelibrary.gsa.gov/ElibMain/scheduleSummary.do?scheduleNumber=70', headers=headers)
data_84 = url_main_84.text
data_70 = url_main_70.text
site_content_84 = bs(data_84)
site_content_70 = bs(data_70)
categories_84 = site_content_84.findAll('tr', {'valign': 'top'})[4:]
cat_num_84 = []
cat_title_84 = []
for x in categories_84:
    try:
        cat_num_84.append(x.a.text)
        cat_title_84.append(x.find('font', {'class': 'columntitle'}).text)
    except:
        pass
categories_70 = site_content_70.findAll('tr', {'valign': 'top'})[4:]
cat_num_70 = []
cat_title_70 = []
for x in categories_70:
    try:
        cat_num_70.append(x.a.text.strip(' - SUBJECT TO COOPERATIVE PURCHASING'))
        cat_title_70.append(x.find('font', {'class': 'columntitle'}).text)
    except:
        pass
link84 = 'https://gsaelibrary.gsa.gov/elib_contracts/schedule_84.xls'
xls84 = pd.read_excel(link84,'Contracts')
link70 = 'https://gsaelibrary.gsa.gov/elib_contracts/schedule_70.xls'
xls70 = pd.read_excel(link70,'Contracts')
xls84.rename(columns = {'Socio-Economic Indicators\n(only relative codes will appear for a contract)':'Small Business','Unnamed: 16':'Other Than Small Business', 'Unnamed: 17':'Woman Owned','Unnamed: 18':'Woman Owned Small Business','Unnamed: 19':'Woman Owned EDWOSB','Unnamed: 20':'Veteran Owned','Unnamed: 21':'Service Disabled Veteran Owned','Unnamed: 22':'Small Disadv','Unnamed: 23':'8(a)','Unnamed: 24':'Hub Zone','Unnamed: 25':'Cooperative Purchasing','Unnamed: 26':'Disaster Recovery' }, inplace = True)
xls84 = xls84[2:]
xls84 = xls84[:-1]
xls70.rename(columns = {'Socio-Economic Indicators\n(only relative codes will appear for a contract)':'Small Business','Unnamed: 16':'Other Than Small Business', 'Unnamed: 17':'Woman Owned','Unnamed: 18':'Woman Owned Small Business','Unnamed: 19':'Woman Owned EDWOSB','Unnamed: 20':'Veteran Owned','Unnamed: 21':'Service Disabled Veteran Owned','Unnamed: 22':'Small Disadv','Unnamed: 23':'8(a)','Unnamed: 24':'Hub Zone','Unnamed: 25':'Cooperative Purchasing','Unnamed: 26':'Disaster Recovery' }, inplace = True)
xls70 = xls70[2:]
xls70 = xls70[:-1]
xls_all = xls84.append(xls70)
xls_all['Category'] = xls_all['Category'].str.strip()
xls_all = xls_all.reset_index(drop=True)
cat_num = cat_num_84 + cat_num_70
cat_title = cat_title_84 + cat_title_70
catdf = pd.DataFrame({'Category' : cat_num, 'Title' : cat_title})
xls_all = pd.merge(xls_all, catdf, on='Category')
xls_all['file_url'] = 0
j = -1
for x in xls_all['Contract #']:
    j = j+1
    xls_all['file_url'][j] = 'https://www.gsaadvantage.gov/ref_text/'+x.replace('-','').strip()+'/'+x.replace('-','').strip()+'_online.htm'
x = xls_all[xls_all['State & Local'] =='Y']
x['Contract #'] = [x.strip() for x in x['Contract #']]
x['id'] = [str(uuid.uuid4()) for x in x['Contract #']]
x['type'] = 'add'
x.set_index('Contract #')
records = x.to_dict('records')
for x in records:
    x['fields'] = dict({
        'associations' : ['General Services Administration'],
        'buyer_lead_agency' : 'General Services Administration',
        'contract_files' : [dict({
            'url' : x['file_url'],
        })],
        'contract_number' : x['Contract #'],
        'cooperative' : 'True',
        'expiration' : x['Contract End Date'],
        'suppliers' : x['Vendor'],
        'supplier_contacts' : [dict({
            'address' : x['Address 1'],
            'city': x['City'],
            'state' : x['State'],
            'zip' : x['Zip'],
            'phone' : x['Phone'],
            'email' : x['Email'],
        })],
        'title' : x['Title'],
        'source_url' : x['file_url'],
    })
records2 = []
for x in records:
    records2.append(dict({ 'id' : x['id'],
            'type' : x['type'],
            'fields' : x['fields'],
           }))
with open('output/gsa8470.json', 'w') as outfile:
    json.dump(records2, outfile)
for x in records2:
    filename = 'output-cloudsearch/'+x['id']+'.json'
    with open(filename, 'w') as outfile:
        json.dump(x, outfile)
