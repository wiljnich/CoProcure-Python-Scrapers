from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime
import json
import uuid
import pandas as pd
from textwrap import wrap
import re

def DecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

headers = headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
url  = requests.get('https://www.1gpa.org/current-vendors/?list_by=alphabetical', headers=headers)
data = url.text
site_content = bs(data)
replaceString = "|"
site_content = bs(str(site_content).replace("<br/>", replaceString))
site_content = bs(str(site_content).replace("<br>", replaceString))
rows = site_content.find('div', {'class': 'row-vendor-categories'})

vendors = site_content.findAll('a', {'class': 'btn btn-default btn-sm'})
suppliers = []
for x in vendors:
    if 'Ordering Informatiom' in x.text:
        pass
    else:
        if '2017-2018' in x.text:
            pass
        else:
            suppliers.append(x.text)
info = site_content.findAll('div', {'class': 'modal-body'})
mass = []
for x in info[1:]:
    mass.append(x.text.replace('\t', '|').replace('\n', '|').replace('|||','|').replace('||', '|').split('Contract: '))
texts = []
for x in mass:
    del x[0]
    for y in x:
        texts.append(y.split('|'))
contract_number = []
for x in texts:
    contract_number.append(x[1])
title = []
for x in texts:
    title.append(x[2].strip(' '))
name = []
for x in texts:
    name.append(x[4].strip(' '))
phone2 = []
for x in texts:
    if x[5][0].isnumeric():
        phone2.append(x[5].strip(' '))
    else:
        if x[6][0] == ' ':
            phone2.append('')
        else:
            if 'email' in x[6]:
                phone2.append(x[5].strip(' '))
            else:
                phone2.append(x[6].strip(' '))
phone = []
for x in phone2:
    phone.append(x.replace('.', '-').replace('/', '-')[0:11])

address = []
for x in texts:
    if 'download' in x[7]:
        address.append(x[6].strip(' '))
    else:
        if '[email\xa0protected]' in x[7]:
            address.append('')
        else:
            address.append(x[7].strip(' '))
expiration = []
for x in texts:
    try:
        if 'Expiration' in x[10]:
            expiration.append(x[11].split('(*')[0])
        else:
            if 'Expiration' in x[11]:
                expiration.append(x[12].split('(*')[0])
            else:
                if 'details' in x[10]:
                    expiration.append(x[10].split('(*')[0])
                else:
                    if 'Extensions' in x[13]:
                        expiration.append(x[16].split('(*')[0])
                    else:
                        expiration.append(x[13].split('(*')[0])
    except IndexError:
        try:
            if 'details' in x[10]:
                expiration.append(x[10].split('(*')[0])
        except IndexError:
            expiration.append(x[7].split('(*')[0])
ebox1 = site_content.findAll('a', {'href' : True})
ebox2 = []
emails = []

for x in ebox1:
    if '/cdn-cgi/' in x['href']:
        ebox2.append(x)
for x in ebox2:
    try:
        if '1gpa.org' in DecodeEmail(x['href'].split('#')[1]) or 'classroomlibrary' in DecodeEmail(x['href'].split('#')[1]) or 'Hartley' in DecodeEmail(x['href'].split('#')[1]) or 'Michelle' in DecodeEmail(x['href'].split('#')[1]):
            pass
        else:
            if '@' not in DecodeEmail(x['href'].split('#')[1]):
                if 'Diana' in DecodeEmail(x['href'].split('#')[1]) or 'Mignoli' in DecodeEmail(x['href'].split('#')[1]):
                    pass
                else:
                    emails.append('')
            else:
                emails.append(DecodeEmail(x['href'].split('#')[1]))
    except IndexError:
        emails.append(DecodeEmail(x['data-cfemail']))

emails.insert(13,'')
emails.insert(195,'')
del emails[283]

cts = site_content.findAll('a', {'class' : 'btn btn-danger btn-block btn-lg'})
for i, j in enumerate(cts[:-1]):
    if j  == cts[i+1]:
        cts[i] = cts[i]
        cts[i+1] = 'XXXX'
cts2 = []
for x in cts:
    if x == 'XXXX':
        pass
    else:
        cts2.append(x)
ct_url = []
ct_name = []
for x in cts2:
    ct_url.append(x['href'])
    try:
        ct_name.append(x['href'].split('/')[7])
    except IndexError:
        ct_name.append('')
ebox2 = site_content.findAll('a', {'class' : 'btn btn-success btn-block'})
exts = []
for x in texts:
    try:
        if 'Contract Extensions' in x[9]:
            exts.append(wrap(x[10], 9))
        else:
            exts.append('')
    except IndexError:
        exts.append('')

amendments = []
j = -1
for x in exts:
    r = []
    for y in x:
        j = j+1
        z = ebox2[j]['href']
        r.append(dict({
            'name' : y,
            'url' : z}))
    amendments.append(r)
x = pd.DataFrame(zip(contract_number, title, suppliers, name, phone, address, emails, ct_name, ct_url, expiration, amendments))
x.columns = ['contract_number', 'title', 'suppliers', 'name', 'phone', 'address', 'emails', 'ct_name', 'ct_url', 'expiration', 'amendments']
x['id'] = [str(uuid.uuid4()) for x in x['contract_number']]
x['type'] = ['add' for x in x['contract_number']]
x['associations'] = ['1Government Procurement Alliance' for x in x['contract_number']]
x.set_index('contract_number')
records = x.to_dict('records')
for x in records:
    x['fields'] = dict({
        'associations' : [x['associations']],
        'amendments_files' : x['amendments'],
        'contract_files' : [dict({
            'name' : x['ct_name'],
            'url' : x['ct_url'],
        })],
        'contract_number' : x['contract_number'],
        'expiration' : x['expiration'],
        'suppliers' : x['suppliers'],
        'supplier_contacts' : [dict({
            'name' : x['name'],
            'address' : x['address'],
            'phone' : x['phone'],
            'email' : x['emails'],
        })],
        'title' : x['title']
    })
    del x['suppliers'], x['name'], x['associations'], x['amendments'], x['ct_name'], x['ct_url'], x['contract_number'], x['expiration'], x['address'], x['phone'], x['emails'], x['title']
with open('output/1gpa.json', 'w') as outfile:
        json.dump(records, outfile)
for x in records:
    filename = 'output-cloudsearch/'+x['id']+'.json'
    with open(filename, 'w') as outfile:
        json.dump(x, outfile)
