from engine import db, Images, Colors
from algorithm import get_image, get_colors
from skimage.color import rgb2lab
import numpy as np

import pandas as pd
import requests  # to get image from the web
import shutil  # to save it locally

CSV_LOCATION = 'csv/dessert'
errorIndex = []
errorURLs = []

df = pd.read_csv(f'{CSV_LOCATION}.csv')
df.dropna(inplace=True)
redList = []
greenList = []
blueList = []

urls = []

for url in df['regular']:
    urls.append(url)

for url in urls:

    index = urls.index(url)
    print(index)
    # download the photo
    try:
        image_url = url
        filename = f'processing_downloaded_photo{str(index)}.jpg'

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(image_url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
                print('Image sucessfully Downloaded: ', filename)

                red, green, blue = get_colors(get_image(filename), 1)[0]
                redList.append(red)
                greenList.append(green)
                blueList.append(blue)

        else:
            print('Image Couldn\'t be retreived')
    except:
        print("There was an error with the file on index {}".format(index))
        print(url)
        errorIndex.append(index)
        errorURLs.append(url)


print("Entering the entry loop")
for index in range(len(redList)):
    if index not in errorIndex:
        print('The loop is currently at {}'.format(index))
        url = df['url'][index]
        regular = df['regular'][index]
        raw = df['raw'][index]
        meta = df['meta'][index]

        if not Images.query.filter_by(url=url).first():
            img = Images(url=url, raw=raw, meta=meta)
            db.session.add(img)

            red = redList[index]
            green = greenList[index]
            blue = blueList[index]

            color = Colors(red=red, green=green, blue=blue, image_url=img.url)
            db.session.add(color)

            db.session.commit()

print("The errors were at: ")
print(errorIndex)
print("and the urls that had error are: ")
print(errorURLs)
