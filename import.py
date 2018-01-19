#!/usr/bin/env python3

import requests
import json
import pymysql.cursors

# Download fresh JSON
file = 'http://auction-api-us.worldofwarcraft.com/auction-data/SECRET_API_KEY/auctions.json'
r = requests.get(file)
with open('auctions.json', 'wb') as f:
  f.write(r.content)

data = json.load(open('auctions.json'))

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='wolf',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
# Truncate the table
   with connection.cursor() as cursor:
        query = "TRUNCATE `items`"
        cursor.execute(query)

# Insert new data from JSON
   with connection.cursor() as cursor:
       index = 0
       while index != None:
           auc = data["auctions"][index]["auc"]
           item = data["auctions"][index]["item"]
           owner = data["auctions"][index]["owner"]
           ownerRealm = data["auctions"][index]["ownerRealm"]
           bid = data["auctions"][index]["bid"]
           buyout = data["auctions"][index]["buyout"]
           quantity = data["auctions"][index]["quantity"]
           timeLeft = data["auctions"][index]["timeLeft"]

           sql = auc, item, owner, ownerRealm, bid, buyout, quantity, timeLeft
           cursor.execute("INSERT INTO items (`auc`, `item`, `owner`, `ownerRealm`, `bid`, `buyout`, `quantity`, `timeLeft`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", sql)
           connection.commit()
           index = index+1

except IndexError:
    pass

# Count number of auctions
with connection.cursor() as cursor:
    query = "SELECT COUNT(`auc`) from `items`"
    cursor.execute(query)
    res = cursor.fetchone()
    print(res)

connection.close()
