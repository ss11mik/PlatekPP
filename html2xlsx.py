# HTML2XLSX pro Platek++;
#  Převod tabulky z webu na XLSX kompatibilní s Platek++;
# použití: python html2xlsx.py dataset/ISKAM.html dataset/ISKAM.xlsx
# autor: ss11mik
# 2025

import pandas as pd
import re
import sys
import math
from bs4 import BeautifulSoup


with open(sys.argv[1], 'r') as file:
    soup = BeautifulSoup(file.read(), features="html.parser")

table = soup.find('table', attrs={'id':'tablePrevodyUhrady'})
table_body = table.find('tbody')

# remove additional instance of menu contents that would make mess in parsing later
for poznamka in table_body.find_all('tr', attrs={'class':'pohledavka-poznamka'}):
    poznamka.extract()


data = []
rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]

    # extract the actual contents of the menu
    popis_menu = row.find('label', attrs={"class": 'popisspoznamkou'})

    # append it to column 'Description'
    if popis_menu is not None:
        cols[3] += ':\n' + str(popis_menu.get('title'))

    # split 1st column into 'Deposited' and 'Submitted at'
    deposited, submitted = str(cols[0].strip()).split(' ', 1)

    # remove seconds
    submitted = ':'.join(submitted.split(':')[:2]) + " " + submitted.split(' ')[1]

    cols = [deposited, submitted] + cols[1:]

    # remove thousands separators
    cols[6] = cols[6].replace(',', '').replace(' ', '')
    cols[7] = cols[7].replace(',', '').replace(' ', '')

    data.append(cols)


df = pd.DataFrame(data, columns=['Deposited', 'Submitted at', 'Billed', 'Type', 'Description', 'Charging', 'Payments', 'Balance'])

df.to_excel(sys.argv[2], index=False)
