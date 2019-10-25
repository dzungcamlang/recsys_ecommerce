import csv
import pandas as pd
from core.models import Item, UserProfile
from django.utils.text import slugify

CSV_PATH = 'D:/workspace/RecSys_ecommerce/recsys/data/product_db.csv'

contSuccess = 0
# Remove all data from Table
Item.objects.all().delete()

db = pd.read_csv(CSV_PATH, sep=";")
print('Loading...')
for idx, row in db.iterrows():
    contSuccess += 1
    Item.objects.create(
        id=contSuccess,
        code=row[0],
        title=row[1],
        price=float(row[2]),
        slug=slugify(row[1]),
        description=row[1])

print(f'{str(contSuccess)} inserted successfully! ')
