from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime
import json
import uuid
import pandas as pd
import urllib
from urllib.request import urlopen
from urllib.request import urlretrieve
import cgi
import re

headers = headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
url  = requests.get("http://www.alliedstatescooperative.com/contracts.php?letter=ALL", headers=headers)
data = url.text
site_content = bs(data)
table = site_content.find('table', {'class': 'table-data'})
rows = table.findAll(lambda tag: tag.name=='td')
sup1 = []
x = ''
child = bs(x)
for child.td in rows[2::5]:
    for child.ul in child.td:
        if child.ul == 'Vendors: ':
            del child.ul
        else:
            sup1.append([child.li.a.text for child.li in child.ul])
suppliers = []
for x in sup1:
    for y in x:
        suppliers.append(y)
associations = [['Allied States Cooperative'] for x in suppliers]
buyer_lead_agency = ['ESC Region 19' for x in suppliers]
contract_number = [x.text for x in rows[0::5]]
title = [x.text for x in rows[1::5]]
cf_1 = ['http://www.alliedstatescooperative.com/' for x in rows[1::5]]
cf_2 = [x.a['href'] for x in rows[1::5]]
cf_url = [a+b for a,b in zip(cf_1,cf_2)]
cf_name = []
for x in cf_url:
    response = urlopen(x)
    blah = response.info()['Content-Disposition']
    value, params = cgi.parse_header(blah)
    filename = params["filename"]
    cf_name.append(filename)
d = pd.DataFrame(zip(associations, buyer_lead_agency, contract_number, title, cf_name, cf_url, sup1))
s = d.apply(lambda x: pd.Series(x[6]),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'r'
d = d.join(s)
d.columns = ['associations', 'buyer_lead_agency', 'contract_number', 'title', 'file_name', 'file_url','to_drop', 'suppliers']
d = d.drop('to_drop', axis=1)
d = d.reset_index()
d = d.drop('index', axis=1)
s_links = []
for child.td in rows[2::5]:
    for child.ul in child.td:
        if child.ul == 'Vendors: ':
            del child.ul
        else:
            u1 = [child.a['href'] for child in child.ul]
            u2 = ['http://www.alliedstatescooperative.com/' for x in u1]
            s_links.append([b+a for a,b in zip(u1,u2)])
name = []
hub_certified = []
phone = []
states = []
notes = []
for y in s_links:
    for x in y:
        headers = headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
        url1  = requests.get(x, headers=headers)
        data1 = url1.text
        site_content1 = bs(data1)
        table1 = site_content1.find('table', {'class': 'table-info'})
        rows1 = table1.findAll(lambda tag: tag.name=='td')
        for child.td in rows1[3::12]:
            hub_certified.append(child.td.text)
        for child.td in rows1[5::12]:
            name.append(child.td.text)
        for child.td in rows1[7::12]:
            num = [str(abs(int(s))) for s in re.findall(r'-?\d+\.?\d*',child.td.text)]
            phone.append('-'.join(num[0:3]))
        for child.td in rows1[9::12]:
            states.append(child.td.text.split(','))
        for child.td in rows1[11::12]:
            notes.append(child.td.text)
sdf = pd.DataFrame(zip(suppliers, name, hub_certified, phone, states, notes))
sdf.columns = ['suppliers','name', 'hub_certified', 'phone_number', 'states', 'notes']
x = sdf.join(d.set_index('suppliers'), on='suppliers')
x = x.reset_index()
x = x.drop('index', axis=1)
x['id'] = [str(uuid.uuid4()) for x in x['suppliers']]
x['type'] = ['add' for x in x['suppliers']]
x.set_index('id')
records = x.to_dict('records')
for x in records:
    x['fields'] = dict({
        'associations' : x['associations'],
        'buyer_lead_agency' : x['buyer_lead_agency'],
        'contract_files' : [dict({
            'name' : x['file_name'],
            'url' : x['file_url']
        })],
        'contract_number' : x['contract_number'],
        'hub_certified' : x['hub_certified'],
        'notes' : x['notes'],
        'geographic_restrictions_allowed_states' : x['states'],
        'states' : 'TX',
        'suppliers' : x['suppliers'],
        'supplier_contacts' : [dict({
            'name' : x['name'],
            'phone' : x['phone_number'],
        })],
        'title' : x['title']
    })
    del x['suppliers'], x['buyer_lead_agency'], x['name'], x['hub_certified'], x['phone_number'], x['states'], x['notes'], x['associations'], x['contract_number'], x['title'], x['file_name'], x['file_url']

with open('output/esc19.json', 'w') as outfile:
    json.dump(records, outfile)
for x in records:
    filename = 'output-cloudsearch/'+x['id']+'.json'
    with open(filename, 'w') as outfile:
        json.dump(x, outfile)
