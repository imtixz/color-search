import requests
import json
import pandas as pd
import os

URL = "https://api.unsplash.com/search/photos"

SEARCHQUERY = 'dessert'

for index in range(10):
    PARAMS = {'query': SEARCHQUERY, 'per_page': '30', 'page': str(
        index+1), 'client_id': os.environ.get('CLIENT_ID')}

    r = requests.get(url=URL, params=PARAMS)

    data = r.json()

    urlList = []
    regularList = []
    rawList = []
    metaList = []

    for i in data['results']:
        url = (i['urls']['small'])
        regular = (i['urls']['regular'])
        raw = (i['urls']['raw'])
        if i['alt_description'] != None:
            meta = i['alt_description']
        elif i['description'] != None:
            meta = i['description']
        else:
            meta = SEARCHQUERY

        urlList.append(url)
        regularList.append(regular)
        rawList.append(raw)
        metaList.append(meta)

    df = pd.DataFrame()

    df['url'] = urlList
    df['regular'] = regularList
    df['raw'] = rawList
    df['meta'] = metaList

    filename = f'{SEARCHQUERY}.csv'

    if index == 0:
        df.to_csv(filename, index=False)
    else:
        with open(filename, 'a') as f:
            df.to_csv(f, index=False, header=False)


# For some reason, the csv files had line gaps after appending.
# Turning them into dataframe and then saving them as csv solves that problem
df = pd.read_csv(filename, encoding='unicode_escape')
df.to_csv(filename, index=False)
