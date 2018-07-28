#!/usr/bin/env python3

import os
from os import system, name

# Install missing imports
os.system('sudo -H pip3 install -r requirements.txt')

import requests
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
# Install Ubuntu Linux python3-pymysql if still cannot import pymysql (bug bypass)
try:
    import pymysql.cursors
except ImportError:
    os.system('sudo -H apt-get install python3-pymysql -y')
    import pymysql.cursors

# Defines the clear function
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

# Query the API for the recently generated Blizzard JSON file URL path
url = requests.get("https://us.api.battle.net/wow/auction/data/stormreaver?locale=en_US&apikey=nv6n8njc8jus3gtrz2n5fw9fpgyfjgcj").content
unicode_str = url.decode("utf8")
encoded_str = unicode_str.encode("ascii",'ignore')
soup = BeautifulSoup(encoded_str, "html.parser")
file = re.findall('(?<=\:\").+?(?=\"\,)', format(soup))
clear()
print ("")
print (file)
print ("")
# I can't get this to automatically set. Possibly related to format(soup) above adding brackets.
file = input("Right click copy the URL above, paste it below, then press enter. \r\n\r\n")


# Downloads the latest auction JSON file
#file = 'http://auction-api-us.worldofwarcraft.com/auction-data/9694c0d6b384d8aa647c840e4c8a3435/auctions.json'
r = requests.get(file)
with open('auctions.json', 'wb') as f:
  f.write(r.content)
data = json.load(open('auctions.json'))


# Connect to the MySQL database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='wolf',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


# Truncate the MySQL 'auctions' table database for a fresh import
try:
   with connection.cursor() as cursor:
        query = "TRUNCATE `auctions`"
        cursor.execute(query)


# Import the latest auction house data from the JSON file into the MySQL 'auctions' table
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
           cursor.execute("INSERT INTO auctions (`auc`, `item`, `owner`, `ownerRealm`, `bid`, `buyout`, `quantity`, `timeLeft`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", sql)
           connection.commit()
           index = index+1
except IndexError:
    pass


# Count number of auctions that were added for a sanity check
with connection.cursor() as cursor:
    query = "SELECT COUNT(`auc`) from `auctions`"
    cursor.execute(query)
    res = cursor.fetchone()
    clear()
    print("Total auction house listings imported: ", res)
    print ("")

# Finito!
connection.close()
