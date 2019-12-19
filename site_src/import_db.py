import csv
import pandas as pd
from core.models import Item, UserProfile, Events
from django.contrib.auth.models import User
from django.utils.text import slugify
import requests
import glob
import shutil
import os


# python manage.py shell
# exec(open('import_db.py').read())


def copy_downloaded_img(src_path, dst_path="./media_root"):
    for jpgfile in glob.iglob(src_path):
        shutil.copy(jpgfile, dst_path)


def get_img(product_name):
    url = 'http://127.0.0.1:5000/api/imageurl'
    params = dict(
        query=product_name,
        nitems=1
    )
    try:
        resp = requests.get(url=url, params=params)
        data = resp.json()
        if data["status"] == 200:
            path = data["url"]
            copy_downloaded_img(path)
            img_name = data["url"].split("\\")[-1]
            return img_name
        else:
            print("No image found 404: {}".format(product_name))
            newname = product_name.split(" ")[:-1]  # remove last word from name
            if len(newname) > 0:
                newname = " ".join(newname)
                return get_img(newname)
            else:
                return "noimage.png"
    except Exception as e:
        print("Error download image '{}'".format(product_name))
        print(e)
        newname = product_name.split(" ")[:-1]  # remove last word from name
        if len(newname) > 0:
            newname = " ".join(newname)
            return get_img(newname)
        else:
            return "noimage.png"


CSV_PATH = 'F:/workspace/RecSys_ecommerce/recsys/data/product_db.csv'

contSuccess = 0
# Remove all data from Table
Item.objects.all().delete()

db = pd.read_csv(CSV_PATH, sep=";", header=None)
print('Loading ITEM data...')
for idx, row in db.iterrows():
    contSuccess += 1
    if contSuccess % 500 == 0:
        print("{} items added".format(contSuccess))
    Item.objects.create(
        id=row[0],
        code=row[1],
        title=row[2],
        price=float(row[4]),
        slug=slugify(row[2]),
        description=row[3],
        image=get_img(row[2]))

print(f'{str(contSuccess)} inserted successfully! ')

# CSV_PATH = 'F:/workspace/RecSys_ecommerce/recsys/data/user_db.csv'
#
# contSuccess = 0
# # Remove all data from Table
# User.objects.all().delete()
#
# db = pd.read_csv(CSV_PATH, sep=";", header=None)
# print('Loading USER data...')
# for idx, row in db.iterrows():
#     contSuccess += 1
#     # if contSuccess > 265965:
#     #     break
#     User.objects.create(
#         password="pbkdf2_sha256$150000$SrfB9cyFbG7m$rNKerOPdIYh6Y3eql+1CK7bvwe5YP40LG+2upQY3KD0=",
#         id=row[0],
#         username=row[1],
#         email="mail_{}@gmail.com".format(row[1]))
#
# print(f'{str(contSuccess)} inserted successfully! ')
#
# CSV_PATH = 'F:/workspace/RecSys_ecommerce/recsys/data/event_db.csv'
#
# contSuccess = 0
# # Remove all data from Table
# Events.objects.all().delete()
#
# db = pd.read_csv(CSV_PATH, sep=";", header=None)
# print('Loading EVENT data...')
# for idx, row in db.iterrows():
#     # try:
#     #     user = User.objects.get(id=row[2])
#     #     item = Item.objects.get(id=row[3])
#     # except Exception as e:
#     #     print(e)
#     #     print(row[2])
#     #     print(row[3])
#     #     print("fail to query")
#     #     continue
#     try:
#         contSuccess += 1
#
#         Events.objects.create(
#             time=row[0],
#             user_id=row[1],
#             item_id=row[2])
#     except Exception as e:
#         print(e)
#         print(row[2])
#         print(row[3])
#         # print(user)
#         # print(item)
#         print("==================================================")
#
#
# print(f'{str(contSuccess)} inserted successfully! ')

# User.objects.create(
#         password="pbkdf2_sha256$150000$SrfB9cyFbG7m$rNKerOPdIYh6Y3eql+1CK7bvwe5YP40LG+2upQY3KD0=",
#         is_superuser=True,
#         is_staff=True,
#         username="trhgnhat",
#         email="trhgnhat@gmail.com")